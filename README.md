# 🚗 AI Car Assistant — RAG + Agent System

An intelligent car assistant that answers questions from a knowledge base and performs calculations, deciding on its own which capability to use for each question. Combines Retrieval-Augmented Generation (RAG) with a tool-calling agent, served through a Streamlit web interface.

Runs on the Google Gemini API free tier, so it needs no local GPU and no paid account.

## ✨ What It Does

Ask a question, and the assistant decides how to answer:

- *"What is a Buyers Guide?"* → searches the car knowledge base (RAG)
- *"Calculate fuel cost for 500 km at 8 L/100km, price 1.5"* → runs the fuel calculator
- *"Monthly payment for a 25000 loan at 5% over 5 years?"* → runs the loan calculator
- *"Estimate total cost of ownership"* → runs the TCO estimator
- *"Hi"* → answers directly, no tool needed
- *"What is the capital of France?"* → politely declines, since it's not a car question

The agent reads each question, picks the right tool (or several) from four available tools, runs them, and composes a natural answer.

## 🏗️ Architecture

```
Documents (docs/*.pdf, *.docx) + cars_knowledge.txt
   ↓  doc_loader.py: convert → clean → chunk → id
   ↓  Gemini embeddings (gemini-embedding-001)
ChromaDB (persistent vector store on disk)

User question (via Streamlit UI)
   ↓
Gemini agent (automatic function calling) picks the tool(s)
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
2. **Remove repeated page footers**: short lines with a page number that repeat on 4+ pages are dropped, so page numbers and booklet titles don't pollute retrieval
3. **Split** with a recursive character splitter (1000 chars, 75 overlap), breaking on paragraphs, then lines, then sentences
4. **Merge short chunks** (under 200 chars) into the next one, so no chunk is left without context
5. **Assign source ids** like `used_car_guide.pdf_chunk_7`, so every retrieved chunk can be traced back to its file

On the FTC guide *Buying a Used Car From a Dealer*, this turned 20 raw chunks ranging from 48 to 4,353 characters into 34 chunks between 201 and 1,167 characters.

The vector store is saved in `chroma_db/`. On each start, chunks that are already stored are skipped, so only new files are embedded.

## 🛡️ Reliability

- **Calibrated relevance threshold:** retrieved chunks with a distance above 0.85 are dropped. The value comes from `calibrate.py`, which compares 10 car questions (best match 0.445–0.699) with 5 off-topic questions (0.991–1.067).
- **Off-topic refusal:** when no chunk passes the threshold, the search tool tells the model to say it only helps with cars, instead of answering from its own memory.
- **Typed, documented tools:** each tool has type hints and a docstring, which the model reads to decide when and how to call it. Inputs are also converted to numbers inside each tool, in case the model sends them as text.
- **API error handling:** if the Gemini API is busy or fails, the user gets a short message instead of a crash.
- **Logging:** the search tool prints its query and retrieval distances for debugging.
- **System prompt rules:** no tools for greetings, never invent numbers, report the tool's number exactly, answer from retrieved text.

## 🛠️ Tech Stack

- **Google Gemini API**: `gemini-3.1-flash-lite-preview` for chat and tool calling, `gemini-embedding-001` for embeddings
- **ChromaDB**: persistent vector database
- **MarkItDown**: converts PDF and Word files to text
- **LangChain Text Splitters**: recursive character chunking
- **Streamlit**: web interface
- **Python 3.12**

## 🔧 Tools

| Tool | Purpose |
|---|---|
| `search_car_knowledge` | RAG search over car problems, maintenance, specs, buying tips |
| `fuel_cost` | Calculate fuel cost for a trip |
| `monthly_payment` | Calculate monthly car loan payment (standard amortization formula) |
| `estimate_tco` | Estimate total cost of ownership (fuel + insurance + maintenance) |

## 🚀 Getting Started

**Prerequisites:** Python 3.12+, a free Gemini API key from [Google AI Studio](https://aistudio.google.com)

```bash
# Install dependencies
pip install -r requirements.txt

# Add your API key (this file is git-ignored)
echo GEMINI_API_KEY=your_key_here > .env

# Run the web app
streamlit run app.py
```

The app opens in your browser at http://localhost:8501. The first start embeds all documents; later starts reuse `chroma_db/`.

## 📁 Project Structure

```
├── app.py               # Streamlit web interface
├── agent.py             # Agent: system prompt, search tool, Gemini call
├── tools.py             # Calculator tools (fuel, loan, TCO)
├── rag.py               # Builds the ChromaDB knowledge base, Gemini client
├── doc_loader.py        # PDF/Word ingestion: convert, clean, chunk, id
├── calibrate.py         # Measures distances to tune the relevance threshold
├── docs/                # Source documents (PDF, Word)
├── cars_knowledge.txt   # Base car knowledge
├── requirements.txt
└── README.md
```

Not committed: `.env` (API key) and `chroma_db/` (rebuilt automatically).

## ⚠️ Known Limitations

- The chat model is a preview version and may change or be retired; the model name is set in one place in `agent.py`.
- Free-tier rate limits apply, and the API sometimes returns "busy" errors during high demand.
- On the free tier, Google may use prompts to improve its products, so don't send private data.
- Changed or deleted files in `docs/` are not detected yet. Delete the `chroma_db/` folder to rebuild the knowledge base. This is also required after changing the embedding model.
- The threshold was calibrated on 15 questions; a larger evaluation set would make it more reliable.

## 🔮 Roadmap

- Deploy online (Hugging Face Spaces)
- Try Gemini's `task_type` option (separate document and query embeddings) and compare retrieval
- Fuel economy data as a pandas tool
- Retrieval evaluation set for the new documents

## 📚 Sources

- Federal Trade Commission, *Buying a Used Car From a Dealer* (consumer.ftc.gov)

## 👤 Author

**Sufian Kanaan** — [LinkedIn](https://linkedin.com/in/sufian-kanaan) · [GitHub](https://github.com/Sufiankanaan)