CALCULATORS = {"fuel_cost", "monthly_payment", "estimate_tco"}

def find_invented_numbers(query, response):
    text= query.replace(",", "")
    invented = []
    for content in (response.automatic_function_calling_history or []):
        for part in (content.parts or []):
            call = part.function_call
            if call and call.name in CALCULATORS:
                for name, value in (call.args or {}).items():
                    forms = {str(value), f"{float(value):g}"}
                    if not any(f in text for f in forms):
                        invented.append(name.replace("_", " "))
    return invented