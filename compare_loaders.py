import re
import sys
from collections import Counter

PDF = "docs/used_car_guide.pdf"


def footer_key(line):
    return re.sub(r"\d+", "#", line.strip()).lower()


def report(name, chunks):
    lengths = [len(c) for c in chunks]
    lines = [l for c in chunks for l in c.splitlines()]
    counts = Counter(footer_key(l) for l in lines
                     if re.search(r"\d", l) and len(l.strip()) <= 100)
    leftovers = {k: n for k, n in counts.items() if n >= 4}
    print(f"[{name}] chunks: {len(chunks)}, shortest: {min(lengths)}, longest: {max(lengths)}")
    print(f"[{name}] repeated footer-like lines left: {leftovers or 'none'}")


def ours():
    from doc_loader import load_and_chunk
    chunks, _ = load_and_chunk(PDF)
    report("ours", chunks)


def unstructured():
    from unstructured.partition.pdf import partition_pdf
    from unstructured.chunking.title import chunk_by_title

    elements = partition_pdf(PDF, strategy="fast")
    print("[unstructured] element types:", Counter(e.category for e in elements))
    kept = [e for e in elements if e.category not in ("Header", "Footer", "PageNumber")]
    chunks = chunk_by_title(kept, max_characters=1000, combine_text_under_n_chars=200)
    report("unstructured", [c.text for c in chunks])


if __name__ == "__main__":
    {"ours": ours, "unstructured": unstructured}[sys.argv[1]]()