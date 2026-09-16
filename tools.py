
def fuel_cost(distance, consumption, price_per_liter):
    distance=float(distance)
    consumption=float(consumption)
    price_per_liter=float(price_per_liter)
    cost = (distance/100)*consumption*price_per_liter
    return round(cost,2)


def monthly_payment(loan_amount,annual_rate,years):
    loan_amount=float(loan_amount)
    annual_rate=float(annual_rate)
    years=float(years)

    monthly_rate = annual_rate/100/12
    months = years*12
    if monthly_rate==0:
        return round(loan_amount/months,2)
    else:
        payment =loan_amount*(monthly_rate*(1+monthly_rate)**months)/((1+monthly_rate)**months-1)
    return round(payment,2)

def estimate_tco(annual_fuel,annual_insurance,annual_maintenance):
    annual_fuel=float(annual_fuel)
    annual_insurance=float(annual_insurance)
    annual_maintenance=float(annual_maintenance)
    tco=annual_fuel+annual_insurance+annual_maintenance
    return round(tco,2)
