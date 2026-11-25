import os
import sys
import chromadb
from dotenv import load_dotenv
from google import genai
from doc_loader import load_and_chunk

load_dotenv()
gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBED_MODEL = "gemini-embedding-001"
BATCH_SIZE = 100
DOC_TYPES = (".pdf", ".docx")

client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH", "chroma_db"))
collection = client.get_or_create_collection(name="cars_docs")


def log(*args):
    print(*args, file=sys.stderr)


def get_embeddings(texts):
    vectors = []
    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]
        result = gemini.models.embed_content(model=EMBED_MODEL, contents=batch)
        vectors.extend(e.values for e in result.embeddings)
    return vectors


def get_embedding(text):
    return get_embeddings([text])[0]


def load_txt_chunks(path="cars_knowledge.txt"):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
    ids = [f"{os.path.basename(path)}_chunk_{i}" for i in range(len(chunks))]
    return chunks, ids


def add_chunks(chunks, ids, existing_ids):
    new = [(doc, doc_id) for doc, doc_id in zip(chunks, ids) if doc_id not in existing_ids]
    if new:
        docs = [doc for doc, _ in new]
        new_ids = [doc_id for _, doc_id in new]
        collection.add(ids=new_ids, embeddings=get_embeddings(docs), documents=docs)
        existing_ids.update(new_ids)
    return len(new), len(chunks) - len(new)


def build_store(docs_dir="docs"):
    existing_ids = set(collection.get(include=[])["ids"])
    log("Already stored:", len(existing_ids))

    sources = [load_txt_chunks()]
    for filename in sorted(os.listdir(docs_dir)):
        if filename.endswith(DOC_TYPES):
            sources.append(load_and_chunk(os.path.join(docs_dir, filename)))

    added = skipped = 0
    for chunks, ids in sources:
        new_count, skip_count = add_chunks(chunks, ids, existing_ids)
        added += new_count
        skipped += skip_count

    log(f"added: {added}, skipped: {skipped}, total: {collection.count()}")
    return added, skipped


if __name__ == "__main__":
    build_store()
    while True:
        query = input("Search the car knowledge base (exit to quit): ")
        if query.lower() == "exit":
            break
        results = collection.query(query_embeddings=[get_embedding(query)], n_results=3)
        for doc_id, dist, doc in zip(results["ids"][0], results["distances"][0], results["documents"][0]):
            print(f"[{dist:.3f}] {doc_id}: {doc[:150]}")
        print("-" * 50)