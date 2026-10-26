try:
    import spaces

    @spaces.GPU
    def _zero_gpu_placeholder():
        pass
except ImportError:
    pass
import gradio as gr
from agent import ask_agent

def respond(message, history):
    return ask_agent(message)

demo = gr.ChatInterface(
    fn=respond,
    title="🚗 AI Car Assistant",
    description="Ask me about car problems, or calculate fuel cost, loan payments, and ownership costs.",
    examples=[
        "What is a Buyers Guide?",
        "Fuel cost for 500 km at 8 L/100km, price 1.5",
        "Monthly payment for a 25000 loan at 5% over 5 years",
    ],
)

demo.launch()