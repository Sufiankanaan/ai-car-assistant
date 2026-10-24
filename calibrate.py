from rag import collection, get_embedding

car_questions = [
    "What is a Buyers Guide?",
    "What does it mean when a car is sold as is?",
    "What is an implied warranty?",
    "Should I get a vehicle history report?",
    "Can I have a used car inspected by my own mechanic?",
    "What should I ask about dealer add-ons?",
    "How do I check a dealer's reputation?",
    "What are common Toyota Camry problems?",
    "How often should I change my oil?",
    "What should I do if I have a problem after buying a car?",
]

off_topic = [
    "What is the capital of France?",
    "How do I bake chocolate cake?",
    "Who won the World Cup?",
    "Write a Python function to reverse a list",
    "What is the weather today?",
]

def best_distance(q):
    r = collection.query(query_embeddings=[get_embedding(q)], n_results=1)
    return r['distances'][0][0]

print("=== CAR ===")
for q in car_questions:
    print(round(best_distance(q), 3), "|", q)

print("=== OFF TOPIC ===")
for q in off_topic:
    print(round(best_distance(q), 3), "|", q)