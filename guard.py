CALCULATORS = {"fuel_cost", "monthly_payment", "estimate_tco"}


def find_invented_in_calls(user_text, calls):
    text = user_text.replace(",", "")
    invented = []
    for call in calls:
        if call["name"] not in CALCULATORS:
            continue
        for name, value in (call.get("args") or {}).items():
            forms = {str(value), f"{float(value):g}"}
            if not any(f in text for f in forms):
                invented.append(name.replace("_", " "))
    return invented


def find_invented_numbers(query, response):
    calls = [
        {"name": part.function_call.name, "args": part.function_call.args}
        for content in (response.automatic_function_calling_history or [])
        for part in (content.parts or [])
        if part.function_call
    ]
    return find_invented_in_calls(query, calls)