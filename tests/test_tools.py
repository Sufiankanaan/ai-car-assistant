import pytest
from tools import fuel_cost,monthly_payment,estimate_tco

@pytest.mark.parametrize("distance, consumption, price, expected", [
    (500, 8, 1.5, 60.0),
    (300, 6.5, 2, 39.0),
    ("500", "8", "1.5", 60.0),
    (123, 7.3, 1.69, 15.17),
])
def test_fuel_cost(distance, consumption, price, expected):
    assert fuel_cost(distance, consumption, price) == expected

def test_monthly_payment():
    assert monthly_payment(25000, 5, 5) == 471.78


def test_monthly_payment_zero_interest():
    assert monthly_payment(1200, 0, 1) == 100.0


def test_estimate_tco():
    assert estimate_tco(1200, 900, 600) == 2700.0
