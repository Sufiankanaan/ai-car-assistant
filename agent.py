
from tools import fuel_cost, monthly_payment, estimate_tco
from rag import collection, get_embedding,gemini
from google.genai import types, errors
import time
from langfuse import observe, get_client
from guard import find_invented_numbers

SYSTEM_PROMPT="""You are a car assistant. You help with car questions and car cost calculations.

Tools:
- search_car_knowledge: use for any question about car problems, maintenance, specs, or buying advice.
- fuel_cost: use when the user gives distance, consumption, and fuel price.
- monthly_payment: use when the user gives loan amount, interest rate, and years.
- estimate_tco: use when the user gives yearly fuel, insurance, and maintenance costs.

Rules:
1. For greetings or small talk like "hi" or "thanks", answer directly. Do not call a tool.
2. Never invent numbers. Only call a calculator when the user gives every number it needs. If one is missing, ask for it and do not call the tool.
3. When a tool returns a number, report that exact number. Never recalculate it yourself.
4. Keep answers short. Do not show formulas.
5. The user cannot see tool results. When search_car_knowledge returns text, only use facts from the search result, do not add facts from your own knowledge.
6. You only help with cars. For any other topic, politely say so and do not answer from your own knowledge.
"""

distance_threshold= 0.85

def search_car_knowledge(query:str)-> str:
    """Search the car knowledge base for info about car problems, maintenance, specs, and buying tips.

    Args:
        query: the search question
    """
    print(f"tool: search_car_knowledge | query: {query}")
    result =collection.query(
        query_embeddings=[get_embedding(query)],
        n_results=3
    )
    docs=result['documents'][0]
    distances =result['distances'][0]
    print("distances: ",distances)
    good_docs=[doc for doc,dist in zip(docs,distances) if dist < distance_threshold]
    
    if not good_docs:
        return "No relevant information found in the car knowledge base. Tell the user I'm here to help you with cars"
    return "\n\n".join(good_docs)

MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
    "gemini-3.1-flash-lite",
] 

CALCULATORS = {"fuel_cost", "monthly_payment", "estimate_tco"}


@observe(name="ask_agent")
def ask_agent(query, return_tools=False):
    langfuse = get_client()
    for model in MODELS:
        for attempt in range(2):
            try:
                response = gemini.models.generate_content(
                    model=model,
                    contents=query,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        tools=[search_car_knowledge, fuel_cost, monthly_payment, estimate_tco],
                    ),
                )
                print(f"model used: {model}")

                tools_used, tool_outputs = [], []
                for content in (response.automatic_function_calling_history or []):
                    for part in (content.parts or []):
                        if part.function_call:
                            tools_used.append(part.function_call.name)
                        if part.function_response:
                            tool_outputs.append(str(part.function_response.response))

                invented = find_invented_numbers(query, response)
                answer = (f"I need the {', '.join(invented)} to calculate that. Could you share it?"
                          if invented else response.text)

                langfuse.update_current_span(
                    input=query,
                    output=answer,
                    metadata={
                        "model": model,
                        "attempt": attempt + 1,
                        "tools": tools_used,
                        "tool_outputs": tool_outputs,
                        "invented_numbers": invented,
                    },
                )
                return (answer, tools_used, tool_outputs) if return_tools else answer
            except errors.APIError as e:
                print(f"{model} failed (attempt {attempt + 1}): {e.code}")
                if e.code in (429, 503):
                    time.sleep(2)
                    continue
                break

    msg = "Sorry, the assistant is very busy right now. Please try again in a minute."
    langfuse.update_current_span(input=query, output=msg, metadata={"error": "all models failed"})
    return (msg, [], []) if return_tools else msg

if __name__=="__main__":
    while True:
        query=input("Ask about cars (calc or info, 'exit' to quit): ")
        if query.lower()=='exit':
            break
        print(ask_agent(query))
        print("-" * 50)
    get_client().flush()




