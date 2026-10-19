# 🚗 AI Car Assistant — RAG + Agent System

An intelligent car assistant that answers questions from a knowledge base and performs calculations, deciding on its own which capability to use for each question. Combines Retrieval-Augmented Generation (RAG) with a tool-calling agent, served through a Streamlit web interface.

Built entirely with local, free tools: no API keys, no token costs.

## ✨ What It Does

Ask a question, and the assistant decides how to answer:

- *"What is a Buyers Guide?"* → searches the car knowledge base (RAG)
- *"Calculate fuel cost for 500 km at 8 L/100km, price 1.5"* → runs the fuel calculator
- *"Monthly payment for a 25000 loan at 5% over 5 years?"* → runs the loan calculator
- *"Estimate total cost of ownership"* → runs the TCO estimator
- *"Hi"* → answers directly, no tool needed

The agent reads each question, picks the right tool (or several) from four available tools, executes them, and composes a natural answer.

## 🏗️ Architecture

```
Documents (docs/*.pdf, *.docx) + cars_knowledge.txt
   ↓  doc_loader.py: convert → clean → chunk → id
ChromaDB (vector store, nomic-embed-text embeddings)

User question (via Streamlit UI)
   ↓
Agent decides which tool(s) to use
   ├─ Knowledge question → search_car_knowledge (RAG + relevance threshold)
   ├─ Fuel question      → fuel_cost
   ├─ Loan question      → monthly_payment
   └─ Ownership question → estimate_tco
   ↓
Tool results returned to the model → natural answer
```

## 📄 Document Ingestion

Any PDF or Word file placed in `docs/` is added to the knowledge base on startup. The pipeline in `doc_loader.py`:

1. **Convert** the file to text with MarkItDown
2. **Remove repeated page footers** with a regex, so page numbers and booklet titles don't pollute retrieval
3. **Split** with a recursive character splitter (1000 chars, 75 overlap), breaking on paragraphs, then lines, then sentences
4. **Merge short chunks** (under 200 chars) into the next one, so no chunk is left without context
5. **Assign source ids** like `used_car_guide.pdf_chunk_7`, so every retrieved chunk can be traced back to its file

On the FTC guide *Buying a Used Car From a Dealer*, this turned 20 raw chunks ranging from 48 to 4,353 characters into 34 chunks between 201 and 1,167 characters.

## 🛡️ Reliability

- **Relevance threshold:** retrieved chunks with an embedding distance above 430 are dropped. Car questions score around 180–230; unrelated questions score above 490.
- **Multiple tool calls:** the agent executes every tool call the model returns, not just the first.
- **Error handling:** tool errors are caught and passed back to the model as text instead of crashing the app.
- **Logging:** each tool name, its arguments, and its result are printed for debugging.
- **System prompt rules:** no tools for greetings, never invent numbers, report the tool's number exactly, answer from retrieved text.

## 🛠️ Tech Stack

- **Ollama**: runs models locally (llama3.2 + nomic-embed-text), fully offline
- **ChromaDB**: vector database for the knowledge base
- **MarkItDown**: converts PDF and Word files to text
- **LangChain Text Splitters**: recursive character chunking
- **Streamlit**: web interface
- **Python**

## 🔧 Tools

| Tool | Purpose |
|---|---|
| `search_car_knowledge` | RAG search over car problems, maintenance, specs, buying tips |
| `fuel_cost` | Calculate fuel cost for a trip |
| `monthly_payment` | Calculate monthly car loan payment (standard amortization formula) |
| `estimate_tco` | Estimate total cost of ownership (fuel + insurance + maintenance) |

## 🚀 Getting Started

**Prerequisites:** Ollama installed and running, Python 3.10+

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

## 📁 Project Structure

```
├── app.py               # Streamlit web interface
├── agent.py             # Agent: tool schemas, system prompt, tool execution
├── tools.py             # Calculator tools (fuel, loan, TCO)
├── rag.py               # Builds the ChromaDB knowledge base
├── doc_loader.py        # PDF/Word ingestion: convert, clean, chunk, id
├── docs/                # Source documents (PDF, Word)
├── cars_knowledge.txt   # Base car knowledge
├── requirements.txt
└── README.md
```

## ⚠️ Known Limitations

- llama3.2 is a small model: it sometimes calls a tool for small talk, and may answer off-topic questions from its own knowledge when the search returns nothing relevant.
- Changed or deleted files in `docs/` are not detected yet. Delete the `chroma_db/` folder to rebuild the knowledge base.
- The relevance threshold (430) was tuned by hand on a small set of questions.

## 🔮 Roadmap

- Deploy online (hosted LLM API + Hugging Face Spaces)
- Fuel economy data as a pandas tool
- Retrieval evaluation set for the new documents

## 📚 Sources

- Federal Trade Commission, *Buying a Used Car From a Dealer* (consumer.ftc.gov)

## 👤 Author

**Sufian Kanaan** — [LinkedIn](https://linkedin.com/in/sufian-kanaan) · [GitHub](https://github.com/Sufiankanaan)