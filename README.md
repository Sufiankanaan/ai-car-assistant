---
title: AI Car Assistant
emoji: 🚗
colorFrom: blue
colorTo: gray
sdk: gradio
sdk_version: "6.30.0"
app_file: gradio_app.py
python_version: "3.12"
pinned: false
license: mit
---
# 🚗 AI Car Assistant — RAG + Agent System
**🔗 Live demo:** https://huggingface.co/spaces/ksufian/ai-car-assistant

An intelligent car assistant that answers questions from a knowledge base and performs calculations, deciding on its own which capability to use for each question. Combines Retrieval-Augmented Generation (RAG) with a tool-calling agent, served through a Gradio chat interface, live on Hugging Face Spaces.

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

User question (via Gradio UI, or Streamlit locally)
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
2. **Remove repeated page footers** with a regex (page number + booklet title), so they don't pollute retrieval. The pattern is specific to the FTC guide; new documents may need their own.
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
- **Model fallback:** if a Gemini model is busy (503) or rate-limited (429), the agent retries and then tries the next model in a tested list.
- **Number guard:** a calculator is only trusted when every number it used appears in the user's question; otherwise the agent asks for the missing value.

## 🛠️ Tech Stack

- **Google Gemini API**: `gemini-3.5-flash-lite` for chat and tool calling (with fallback models), `gemini-embedding-001` for embeddings
- **ChromaDB**: persistent vector database
- **MarkItDown**: converts PDF and Word files to text
- **LangChain Text Splitters**: recursive character chunking
- **Gradio**: chat interface, deployed on Hugging Face Spaces
- **Streamlit**: local chat interface
- **Python 3.12**
- **Langfuse**: tracing and observability

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

## 🧪 Tests

Fast unit tests cover the deterministic parts: the three calculators and the number guard.
They use a fake Gemini response, so they need no API key and no quota.

```bash
pytest -v
```

11 tests, under a second. The slower LLM evals (`run_evals.py`, `judge.py`) are run before a merge.

## 📏 Evaluation

The agent is tested with a 15-question golden set (`eval_set.json`) and two scripts:

- **`run_evals.py`** checks each answer end to end: the right tool, required keywords, and forbidden ones (for example, no "Paris" for an off-topic question, and no made-up result when a number is missing).
- **`judge.py`** uses a second Gemini model as an LLM judge to check **faithfulness**: is every claim in a search answer supported by the retrieved chunks?

| Metric | Baseline | Now |
|---|---|---|
| End-to-end score | 14/15 | 15/15 |
| Faithfulness (search answers) | 6/7 | 7/7 |

What the evals caught:
- Off-topic questions were answered from memory, because the refusal only lived inside the search tool → added a "cars only" rule to the system prompt.
- A search answer added a fact that wasn't in the retrieved text → tightened the rule to answer only from the search result.
- The model sometimes invented a missing fuel price, even after prompt rules → added a code guard: every number sent to a calculator must appear in the user's question.

LLM answers vary between runs, so results are checked over several runs, per question, not only by the total score.

## 🔭 Observability

Every request is traced with [Langfuse](https://langfuse.com): the question, the answer, the model used, the tools called, the retrieved chunks, and any numbers the guard flagged.

## 📁 Project Structure

```
├── gradio_app.py          # Gradio chat UI (live on Hugging Face Spaces)
├── app.py                 # Streamlit chat UI (local)
├── agent.py               # Agent: system prompt, search tool, Gemini call, model fallback, Langfuse tracing
├── tools.py               # Calculator tools (fuel, loan, TCO)
├── guard.py               # Number guard: blocks calculator numbers not found in the question
├── rag.py                 # Builds the ChromaDB knowledge base, Gemini client
├── doc_loader.py          # PDF/Word ingestion: convert, clean, chunk, id
├── calibrate.py           # Measures distances to tune the relevance threshold
├── eval_set.json          # 15-question golden set for evaluation
├── run_evals.py           # End-to-end evals: tool, required and forbidden keywords
├── judge.py               # LLM-as-judge: checks answers are supported by retrieved text
├── conftest.py            # Tells pytest where the project root is
├── tests/
│   ├── test_tools.py      # Unit tests for the calculators
│   └── test_guard.py      # Unit tests for the number guard (fake Gemini response, no API calls)
├── docs/                  # Source documents (PDF, Word)
├── cars_knowledge.txt     # Base car knowledge
├── requirements.txt       # Dependencies
├── requirements-lock.txt  # Exact working versions (pip freeze)
└── README.md
```

Not committed: `.env` (API keys) and `chroma_db/` (rebuilt automatically).

## ⚠️ Known Limitations

- On the free tier, each Gemini model has a small daily request limit and is sometimes busy, so the live demo and eval runs can hit it. The agent falls back to other models, but if all are limited, it asks the user to try again.
- On the free tier, Google may use prompts to improve its products, so don't send private data.
- Changed or deleted files in `docs/` are not detected yet. Delete the `chroma_db/` folder to rebuild the knowledge base. This is also required after changing the embedding model.
- The threshold was calibrated on 15 questions; a larger evaluation set would make it more reliable.

## 🔮 Roadmap

- Try Gemini's `task_type` option (separate document and query embeddings) and compare retrieval
- Fuel economy data as a pandas tool
- Retrieval evaluation set for the new documents

## 📚 Sources

- Federal Trade Commission, *Buying a Used Car From a Dealer* (consumer.ftc.gov)

## 👤 Author

**Sufian Kanaan** — [LinkedIn](https://linkedin.com/in/sufian-kanaan) · [GitHub](https://github.com/Sufiankanaan)