
from tools import fuel_cost, monthly_payment, estimate_tco
from rag import collection, get_embedding,gemini
from google.genai import types


SYSTEM_PROMPT="""You are a car assistant. You help with car questions and car cost calculations.

Tools:
- search_car_knowledge: use for any question about car problems, maintenance, specs, or buying advice.
- fuel_cost: use when the user gives distance, consumption, and fuel price.
- monthly_payment: use when the user gives loan amount, interest rate, and years.
- estimate_tco: use when the user gives yearly fuel, insurance, and maintenance costs.

Rules:
1. For greetings or small talk like "hi" or "thanks", answer directly. Do not call a tool.
2. Never invent numbers. If a number is missing, ask the user for it.
3. When a tool returns a number, report that exact number. Never recalculate it yourself.
4. Keep answers short. Do not show formulas.
5. The user cannot see tool results. When search_car_knowledge returns text, answer the user's question using that text, in your own words.
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


def ask_agent(query):
    try:
        response= gemini.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[search_car_knowledge, fuel_cost, monthly_payment, estimate_tco],
            ),
        )
        return response.text
    except Exception as e:
        return f"Sorry, the model is busy. Try again. ({e})"


if __name__=="__main__":
    while True:
        query=input("Ask about cars (calc or info, 'exit' to quit): ")
        if query.lower()=='exit':
            break
        print(ask_agent(query))
        print("-" * 50)




