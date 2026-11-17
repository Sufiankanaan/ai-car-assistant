import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware, ModelRetryMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.langchain import CallbackHandler
from langgraph.checkpoint.memory import InMemorySaver

from agent import SYSTEM_PROMPT, search_car_knowledge
from guard import find_invented_in_calls
from tools import fuel_cost, monthly_payment, estimate_tco

load_dotenv()

MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
    "gemini-3.1-flash-lite",
]


def make_model(name):
    return ChatGoogleGenerativeAI(model=name, google_api_key=os.getenv("GEMINI_API_KEY"))


graph = create_agent(
    model=make_model(MODELS[0]),
    tools=[search_car_knowledge, fuel_cost, monthly_payment, estimate_tco],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver(),
    middleware=[
        ModelFallbackMiddleware(*[make_model(m) for m in MODELS[1:]]),
        ModelRetryMiddleware(max_retries=2, initial_delay=2.0, on_failure="error"),
    ],
)

BUSY = "Sorry, the assistant is very busy right now. Please try again in a minute."


def ask_graph(query, thread_id="default", return_tools=False):
    try:
        result = graph.invoke(
            {"messages": [{"role": "user", "content": query}]},
            {"configurable": {"thread_id": thread_id}, "callbacks": [CallbackHandler()]},
        )
    except Exception as e:
        print(f"All models failed: {e}")
        return (BUSY, [], []) if return_tools else BUSY

    messages = result["messages"]
    content = messages[-1].content
    if isinstance(content, list):
        content = "".join(p.get("text", "") for p in content if isinstance(p, dict))

    user_text = "\n".join(str(m.content) for m in messages if m.type == "human")
    calls = [call for m in messages for call in (getattr(m, "tool_calls", None) or [])]
    invented = find_invented_in_calls(user_text, calls)
    if invented:
        content = f"I need the {', '.join(invented)} to calculate that. Could you share it?"

    if return_tools:
        tool_outputs = [str(m.content) for m in messages if m.type == "tool"]
        return content, [c["name"] for c in calls], tool_outputs
    return content


if __name__ == "__main__":
    from langfuse import get_client
    print(ask_graph("Fuel cost for 500 km at 8 L/100km", thread_id="test-1"))
    print("-" * 50)
    print(ask_graph("3.20", thread_id="test-1"))
    get_client().flush()