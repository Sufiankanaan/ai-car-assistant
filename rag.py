import ollama
import chromadb
import os
from doc_loader import load_and_chunk

with open('cars_knowledge.txt','r',encoding='utf-8') as f :
    content=f.read()

chunk=[c.strip() for c in content.split('\n\n')if c.strip()]

client = chromadb.Client()

collection = client.get_or_create_collection(name='cars_docs')

def get_embedding(text):
    return ollama.embeddings(model='nomic-embed-text',prompt=text)['embedding']

for i ,doc in enumerate(chunk):
    collection.add(
        ids=[f"cars_knowledge.txt_chunk_{i}"],
        embeddings=[get_embedding(doc)],
        documents=[doc]
    )

for filename in os.listdir("docs"):

    if not filename.endswith((".pdf", ".docx")):
        continue   

    path = os.path.join("docs", filename)  

    chunks, ids = load_and_chunk(path) 
    for doc, doc_id in zip(chunks, ids):
        collection.add(
            ids=[doc_id],
            embeddings=[get_embedding(doc)],
            documents=[doc]
        )

print("Total in collection:", collection.count())

if __name__=='__main__':
    while True:

        query=input("Ask me about car (to exit ->exit): ")
        if query.lower()=='exit':
            break

        results = collection.query(
            query_embeddings=[get_embedding(query)],
            n_results=3
        )

        retrieved_context =results['documents'][0]
        source_id =results['ids'][0]
        for idx,doc in zip(source_id,retrieved_context):
            print(f"📄 {idx} : {doc}")
        print(50*"-")

        context='\n\n'.join(retrieved_context)
        prompt=f"""Answer the question based ONLY on the following context.
        If the context doesn't contain the answer, say so.
        context:{context}
        question:{query}
        Answer:"""

        response=ollama.chat(model='llama3.2',
                             messages=[{'role':'user','content':prompt}])

        print(response['message']['content'])

        print(45*'-')




