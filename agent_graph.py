import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from agent import SYSTEM_PROMPT, search_car_knowledge
from tools import fuel_cost, monthly_payment, estimate_tco

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

graph = create_agent(
    model=model,
    tools=[search_car_knowledge, fuel_cost, monthly_payment, estimate_tco],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver(),
)


def ask_graph(query, thread_id="default", return_tools=False):
    result = graph.invoke(
        {"messages": [{"role": "user", "content": query}]},
        {"configurable": {"thread_id": thread_id}},
    )
    messages = result["messages"]
    content = messages[-1].content
    if isinstance(content, list):
        content = "".join(p.get("text", "") for p in content if isinstance(p, dict))

    if return_tools:
        tools_used = [call["name"] for m in messages for call in (getattr(m, "tool_calls", None) or [])]
        tool_outputs = [str(m.content) for m in messages if m.type == "tool"]
        return content, tools_used, tool_outputs
    return content

if __name__ == "__main__":
    print(ask_graph("Fuel cost for 500 km at 8 L/100km", thread_id="test-1"))
    print("-" * 50)
    print(ask_graph("3.20", thread_id="test-1"))