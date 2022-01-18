from decimal import Decimal

factor = Decimal(1000000)
stretch = Decimal(100)
max_supply = factor


def token_formula(x: Decimal) -> Decimal:
    return -(factor*stretch)/(x+stretch) + factor


def inverse_token_formula(y: Decimal) -> Decimal:
    return (factor*stretch)/(factor-y) - stretch


def price_for_1_token(y: Decimal) -> Decimal:
    return inverse_token_formula(y+1) - inverse_token_formula(y)
