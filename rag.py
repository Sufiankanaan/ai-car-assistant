import ollama
import chromadb

with open('cars_knowledge.txt','r',encoding='utf-8') as f :
    content=f.read()

chunk=[c.strip() for c in content.split('\n\n')if c.strip()]

client = chromadb.Client()

collection = client.get_or_create_collection(name='cars_docs')

def get_embedding(text):
    return ollama.embeddings(model='nomic-embed-text',prompt=text)['embedding']

for i ,doc in enumerate(chunk):
    collection.add(
        ids=[str(i)],
        embeddings=[get_embedding(doc)],
        documents=[doc]
    )


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
            print(f"📄 Source #{int(idx)+1} : {doc}")
        print(50*"-")

        prompt=f"""Answer the question based ONLY on the following context.
        If the context doesn't contain the answer, say so.
        context:{'\n\n'.join(retrieved_context)}
        question:{query}
        Answer:"""

        response=ollama.chat(model='llama3.2',
                             messages=[{'role':'user','content':prompt}])

        print(response['message']['content'])

        print(45*'-')




