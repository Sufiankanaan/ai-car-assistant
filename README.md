# 🚗 AI Car Assistant — RAG + Agent System

An intelligent car assistant that **answers questions from a knowledge base** and **performs calculations** — deciding on its own which capability to use for each question. Combines Retrieval-Augmented Generation (RAG) with tool-calling agents, served through a Streamlit web interface.

Built entirely with **local, free tools** — no API keys, no token costs.

---

## ✨ What It Does

Ask a question, and the assistant automatically decides how to answer:

- **"What are common Toyota Camry problems?"** → searches the car knowledge base (RAG)
- **"Calculate fuel cost for 500 km at 8 L/100km, price 1.5"** → runs the fuel calculator
- **"Monthly payment for a 25000 loan at 5% over 5 years?"** → runs the loan calculator
- **"Estimate total cost of ownership"** → runs the TCO estimator

The agent reads each question, picks the right tool from four available tools, executes it, and composes a natural answer.

---

## 🏗️ Architecture

```
User question (via Streamlit UI)
   ↓
Agent decides which tool to use (from 4 tools)
   ├─ Knowledge question → search_car_knowledge (RAG over ChromaDB)
   ├─ Fuel question      → fuel_cost calculator
   ├─ Loan question      → monthly_payment calculator
   └─ Ownership question → estimate_tco calculator
   ↓
Tool executes → result returned to the model → natural answer
```

This project integrates two AI engineering capabilities into one system:
- **RAG** — semantic search over a car knowledge base, grounded and hallucination-resistant.
- **Tool-calling agent** — the model autonomously selects and calls the right calculator.

---

## 🛠️ Tech Stack

- **Ollama** — runs models locally (llama3.2 + nomic-embed-text), fully offline
- **ChromaDB** — vector database for the RAG knowledge base
- **Streamlit** — web interface
- **Python**

---

## 🔧 Capabilities (Tools)

| Tool | Purpose |
|------|---------|
| `search_car_knowledge` | RAG search over car problems, maintenance, specs, buying tips |
| `fuel_cost` | Calculate fuel cost for a trip |
| `monthly_payment` | Calculate monthly car loan payment (standard amortization formula) |
| `estimate_tco` | Estimate total cost of ownership (fuel + insurance + maintenance) |

---

## 🚀 Getting Started

### Prerequisites
- [Ollama](https://ollama.com) installed and running
- Python 3.10+

### Setup

```bash
# Install Ollama models
ollama pull llama3.2
ollama pull nomic-embed-text

# Install dependencies
pip install -r requirements.txt

# Run the web app
streamlit run app.py
```

The app opens in your browser at http://localhost:8501

---

## 📁 Project Structure

```
├── app.py            # Streamlit web interface
├── agent.py          # The agent: tool schemas, decision logic, tool execution
├── tools.py          # Calculator tools (fuel, loan, TCO)
├── rag.py            # RAG pipeline (ChromaDB + embeddings)
├── cars_knowledge.txt # Car knowledge base
├── requirements.txt
└── README.md
```

---

## 🔑 Key Concepts Demonstrated

- **RAG + Agent integration** — combining retrieval and tool-calling in one system
- **Tool-calling** — an LLM autonomously selecting the right tool per question
- **Semantic search** — matching questions to knowledge by meaning
- **Grounded answers** — the RAG tool reduces hallucination by answering from sources
- **Clean architecture** — separated modules (RAG, tools, agent, UI)
- **Full-stack AI** — from knowledge base to web interface

---

## 🔮 Roadmap

- Multi-agent workflow (router → retrieval → synthesizer)
- Real-time parts pricing via external APIs
- Larger, PDF-based knowledge base
- Model Context Protocol (MCP) for standardized tool integration

---

## 👤 Author
**Sufian Kanaan** — [LinkedIn](https://www.linkedin.com/in/sufian-kanaan/)