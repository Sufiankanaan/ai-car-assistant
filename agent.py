import ollama
from tools import fuel_cost, monthly_payment, estimate_tco
from rag import collection, get_embedding

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'search_car_knowledge',
            'description': 'Search car knowledge base for info about car problems, maintenance, specs, buying tips',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string', 'description': 'the search question'}
                },
                'required': ['query']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'fuel_cost',
            'description': 'Calculate fuel cost for a trip',
            'parameters': {
                'type': 'object',
                'properties': {
                    'distance': {'type': 'number', 'description': 'distance in km'},
                    'consumption': {'type': 'number', 'description': 'liters per 100km'},
                    'price_per_liter': {'type': 'number', 'description': 'fuel price per liter'}
                },
                'required': ['distance', 'consumption', 'price_per_liter']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'monthly_payment',
            'description': 'Calculate monthly car loan payment',
            'parameters': {
                'type': 'object',
                'properties': {
                    'loan_amount': {'type': 'number', 'description': 'loan amount'},
                    'annual_rate': {'type': 'number', 'description': 'annual interest rate percent'},
                    'years': {'type': 'number', 'description': 'loan term in years'}
                },
                'required': ['loan_amount', 'annual_rate', 'years']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'estimate_tco',
            'description': 'Estimate total cost of ownership (fuel + insurance + maintenance)',
            'parameters': {
                'type': 'object',
                'properties': {
                    'annual_fuel': {'type': 'number', 'description': 'annual fuel cost'},
                    'annual_insurance': {'type': 'number', 'description': 'annual insurance'},
                    'annual_maintenance': {'type': 'number', 'description': 'annual maintenance'}
                },
                'required': ['annual_fuel', 'annual_insurance', 'annual_maintenance']
            }
        }
    }
]

SYSTEM_PROMPT="""You are a car assistant. You help with car questions and car cost calculations.

Tools:
- search_car_knowledge: use for any question about car problems, maintenance, specs, or buying advice.
- fuel_cost: use when the user gives distance, consumption, and fuel price.
- monthly_payment: use when the user gives loan amount, interest rate, and years.
- estimate_tco: use when the user gives yearly fuel, insurance, and maintenance costs.

Rules:
1. For greetings or small talk like "hi" or "thanks", answer directly. Do not call a tool.
2. Never invent numbers. If a number is missing, ask the user for it.
3. When a tool returns a number, report that exact number. Never recalculate it yourself.
4. Keep answers short. Do not show formulas.
"""

distance_threshold= 430

def execute_tool(tool_name, arguments):
    if tool_name =='search_car_knowledge':
        results= collection.query(
            query_embeddings=[get_embedding(arguments['query'])],
            n_results=3
        )
        docs=results['documents'][0]
        distances=results['distances'][0]

        good_docs=[doc for doc,dist in zip(docs,distances) if dist < distance_threshold]

        if not good_docs:
            return" I'm here to help you with cars"
        return "\n\n".join(results['documents'][0])

    elif tool_name == 'fuel_cost':
        return fuel_cost(**arguments)

    elif tool_name == 'monthly_payment':
        return monthly_payment(**arguments)

    elif tool_name == 'estimate_tco':
        return estimate_tco(**arguments)

    else:
        return f"Error: unknown tool {tool_name}"

def ask_agent(query):
    messages = [{'role':'system','content':SYSTEM_PROMPT},
                {'role': 'user', 'content': query}]
    response = ollama.chat(model='llama3.2', messages=messages, tools=tools)
    if response['message'].tool_calls:
        print(len(response['message'].tool_calls))
        messages.append(response['message'])
        for call in response['message'].tool_calls:
            tool_name = call.function.name
            arguments = call.function.arguments
            print(f'tool name {tool_name} arguments {arguments}')   
            result = execute_tool(tool_name, arguments)
            print(result)
            messages.append({'role': 'tool', 'content': str(result)})
        final = ollama.chat(model='llama3.2', messages=messages)
        return final['message']['content']
        
    else:
        return response['message']['content']


if __name__=="__main__":
    while True:
        query=input("Ask about cars (calc or info, 'exit' to quit): ")
        if query.lower()=='exit':
            break
        print(ask_agent(query))
        print("-" * 50)




