from markitdown import MarkItDown
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
import os
from collections import Counter

md =MarkItDown(enable_plugins=False)
MIN_LEN=200
FOOTER_MIN_REPEATS=4
FOOTER_MAX_LEN=100

splitter =RecursiveCharacterTextSplitter(
    
    length_function=len,
    chunk_size=1000,
    chunk_overlap=75,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ],
)

# a footer is a short line with a page number that repeats on many pages,
# so compare lines with their digits masked
def footer_key(line):
    return re.sub(r"\d+","#",line.strip()).lower()

def remove_footers(text):
    lines=text.splitlines()
    counts=Counter(footer_key(l) for l in lines
                   if re.search(r"\d",l) and len(l.strip())<=FOOTER_MAX_LEN)
    footers={k for k,n in counts.items() if n>=FOOTER_MIN_REPEATS}
    cleaned="\n".join(l for l in lines if footer_key(l) not in footers)
    return re.sub(r"\n{3,}","\n\n",cleaned)


def merge_short(chunks,min_len=MIN_LEN):
    merged=[]
    buffer=""
    for chunk in chunks:
        buffer=f'{buffer}\n{chunk}'.strip()if buffer else chunk
        if len(buffer)>=min_len:
            merged.append(buffer)
            buffer=""
    if buffer:
        if merged:
            merged[-1]+='\n'+buffer
        else:
            merged.append(buffer)
    return merged

def make_ids(file_path, chunks):
    name = os.path.basename(file_path)
    return[f'{name}_chunk_{i}' for i in range(len(chunks))]

def load_and_chunk(file_path):
    text=md.convert(file_path).markdown
    text = remove_footers(text)
    chunks = [c.strip() for c in splitter.split_text(text) if c.strip()]
    chunks = merge_short(chunks)                             # فراغ 2
    ids = make_ids(file_path, chunks)
    return chunks,ids 

if __name__ == "__main__":
    chunks, ids = load_and_chunk("docs/used_car_guide.pdf")
    print(len(chunks), ids[0], ids[-1])
