from types import SimpleNamespace
from guard import find_invented_numbers


def fake_response(tool_name, args):
    call = SimpleNamespace(name=tool_name, args=args)
    part = SimpleNamespace(function_call=call)
    content = SimpleNamespace(parts=[part])
    return SimpleNamespace(automatic_function_calling_history=[content])


def test_all_numbers_given():
    response = fake_response("fuel_cost", {"distance": 500, "consumption": 8, "price_per_liter": 1.5})
    assert find_invented_numbers("Fuel cost for 500 km at 8 L/100km, price 1.5", response) == []


def test_missing_price_is_caught():
    response = fake_response("fuel_cost", {"distance": 500, "consumption": 8, "price_per_liter": 1.5})
    assert find_invented_numbers("Fuel cost for 500 km at 8 L/100km", response) == ["price per liter"]


def test_comma_in_number():
    response = fake_response("monthly_payment", {"loan_amount": 25000, "annual_rate": 5, "years": 5})
    assert find_invented_numbers("Monthly payment for a 25,000 loan at 5% over 5 years", response) == []


def test_search_tool_is_ignored():
    response = fake_response("search_car_knowledge", {"query": "Buyers Guide 999"})
    assert find_invented_numbers("What is a Buyers Guide?", response) == []