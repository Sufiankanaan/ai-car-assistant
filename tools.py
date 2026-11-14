
def fuel_cost(distance: float, consumption: float, price_per_liter: float)-> float:
    """Calculate fuel cost for a trip.

        Args:
            distance: distance in km
            consumption: liters per 100km
            price_per_liter: fuel price per liter
    """
    distance=float(distance)
    consumption=float(consumption)
    price_per_liter=float(price_per_liter)
    cost = (distance/100)*consumption*price_per_liter
    return round(cost,2)


def monthly_payment(loan_amount: float,annual_rate: float,years: float)->float:
    """Calculate monthly car loan payment.
    
        Args:
            loan_amount: loan amount
            annual_rate: annual interest rate percent
            years: loan term in years
    """
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

def estimate_tco(annual_fuel: float,annual_insurance: float,annual_maintenance: float)->float:
    """Estimate total cost of ownership (fuel + insurance + maintenance).
    
        Args:
            annual_fuel: annual fuel cost
            annual_insurance: annual insurance
            annual_maintenance: annual maintenance
    """
    annual_fuel=float(annual_fuel)
    annual_insurance=float(annual_insurance)
    annual_maintenance=float(annual_maintenance)
    tco=annual_fuel+annual_insurance+annual_maintenance
    return round(tco,2)
