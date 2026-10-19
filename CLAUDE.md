# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A local, offline car assistant: a tool-calling agent (Ollama `llama3.2`) that answers from a RAG knowledge base (ChromaDB + `nomic-embed-text` embeddings) or runs calculator tools, served through Streamlit. No API keys; everything runs against a local Ollama server.

## Commands

Prerequisites: Ollama running locally with `llama3.2` and `nomic-embed-text` pulled, Python 3.10+ (the local `venv/` is 3.12). Keep code 3.10-compatible, for example no backslashes inside f-string expressions.

```bash
pip install -r requirements.txt   # keep this file UTF-8; PowerShell `>` writes UTF-16
streamlit run app.py              # web UI at http://localhost:8501
python agent.py                   # CLI loop through the full agent (prints tool names, args, results)
python rag.py                     # CLI loop for plain RAG: shows retrieved chunk ids, no tools
python doc_loader.py              # chunk docs/used_car_guide.pdf and print chunk count and first/last id
```

There are no tests, linter, or build step. Run every command from the repo root, because `rag.py` opens `cars_knowledge.txt` and `docs/` with relative paths.

## Architecture

Dependency chain: `app.py` → `agent.py` → `rag.py` → `doc_loader.py`, and `agent.py` → `tools.py`.

- **`rag.py` builds the index as an import side effect.** Importing it embeds `cars_knowledge.txt` (split on blank lines) and every `.pdf`/`.docx` in `docs/` into an in-memory `chromadb.Client()` collection `cars_docs`. Any `import rag` or `import agent` therefore needs Ollama up and re-embeds everything, with no persistence. `agent.py` imports `collection` and `get_embedding` from it.
- **`doc_loader.load_and_chunk(path)`**: MarkItDown → `remove_footers` → `RecursiveCharacterTextSplitter` (1000 chars, 75 overlap) → `merge_short` (combines chunks under 200 chars) → ids of the form `<filename>_chunk_<i>`. `remove_footers` works for any document: it drops lines of up to 100 characters that contain a digit and repeat at least 4 times with their digits masked. A footer without a page number is not caught. On the FTC guide, the expected output is 34 chunks of 201–1,167 characters.
- **`agent.ask_agent(query)`** makes a single round of tool calling: one `ollama.chat` with the `tools` schemas, then it runs **every** returned tool call and appends each result as a `tool` message, followed by one final `ollama.chat` without tools. There is no multi-step loop. Tool exceptions are caught and sent to the model as text.
- **RAG relevance gate**: `search_car_knowledge` in `execute_tool` queries the top 3 and drops chunks with distance ≥ `distance_threshold` (430, tuned by hand: car questions score about 180–230, off-topic ones above 490). If nothing passes, it returns a fixed "I'm here to help you with cars" string.

### Adding or changing a tool

A tool is defined in four places in `agent.py`/`tools.py`, and they must stay in sync:
1. The function in `tools.py`. Existing tools cast their inputs with `float()` because the model may pass strings, and round results to 2 decimals.
2. A JSON schema entry in the `tools` list in `agent.py`.
3. A branch in `execute_tool`.
4. A line in `SYSTEM_PROMPT`. Its rules (no tools for small talk, never invent or recompute numbers, answer from retrieved text) were written to work around weaknesses of the small `llama3.2` model.

## Notes

- `data_later/` (fuel economy xlsx/md) is untracked and set aside for the planned "fuel economy as a pandas tool" roadmap item. It is not loaded anywhere yet.
- Debug output goes through `print` (retrieval distances, tool calls, results), so it shows in the terminal that runs Streamlit, not in the UI.
