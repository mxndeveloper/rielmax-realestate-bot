def calculate_monthly_payment(price: float, down_payment: float, annual_rate: float, years: int = 30) -> float:
    """
    Calculate monthly mortgage payment.
    annual_rate: in percent (e.g., 21 for 21%)
    """
    loan_amount = price - down_payment
    if loan_amount <= 0:
        return 0
    monthly_rate = annual_rate / 100 / 12
    months = years * 12
    if monthly_rate == 0:
        return loan_amount / months
    payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return round(payment, 2)