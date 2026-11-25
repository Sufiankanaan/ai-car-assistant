import os
import tempfile
from types import SimpleNamespace

os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("CHROMA_PATH", tempfile.mkdtemp())

import rag  # noqa: E402


class FakeCollection:
    def __init__(self):
        self.added = []

    def add(self, ids, embeddings, documents):
        self.added.append(ids)


def fake_embeddings(texts):
    return [[0.0] for _ in texts]


def test_add_chunks_skips_existing_ids(monkeypatch):
    fake = FakeCollection()
    monkeypatch.setattr(rag, "collection", fake)
    monkeypatch.setattr(rag, "get_embeddings", fake_embeddings)
    existing = {"a_chunk_0"}

    added, skipped = rag.add_chunks(["old", "new"], ["a_chunk_0", "a_chunk_1"], existing)

    assert (added, skipped) == (1, 1)
    assert fake.added == [["a_chunk_1"]]
    assert "a_chunk_1" in existing


def test_nothing_new_means_no_api_call(monkeypatch):
    fake = FakeCollection()
    monkeypatch.setattr(rag, "collection", fake)
    monkeypatch.setattr(rag, "get_embeddings", fake_embeddings)

    added, skipped = rag.add_chunks(["old"], ["a_chunk_0"], {"a_chunk_0"})

    assert (added, skipped) == (0, 1)
    assert fake.added == []


def test_embeddings_are_sent_in_batches(monkeypatch):
    sizes = []

    def embed_content(model, contents):
        sizes.append(len(contents))
        return SimpleNamespace(embeddings=[SimpleNamespace(values=[0.0]) for _ in contents])

    monkeypatch.setattr(rag, "gemini", SimpleNamespace(models=SimpleNamespace(embed_content=embed_content)))

    vectors = rag.get_embeddings(["text"] * 250)

    assert sizes == [100, 100, 50]
    assert len(vectors) == 250


def test_txt_ids_keep_the_old_format(tmp_path):
    f = tmp_path / "cars_knowledge.txt"
    f.write_text("first\n\n\n\nsecond\n\n  \n\nthird", encoding="utf-8")

    chunks, ids = rag.load_txt_chunks(str(f))

    assert chunks == ["first", "second", "third"]
    assert ids == ["cars_knowledge.txt_chunk_0", "cars_knowledge.txt_chunk_1", "cars_knowledge.txt_chunk_2"]