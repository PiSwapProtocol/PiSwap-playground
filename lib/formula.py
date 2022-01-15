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


def calculate_new_weights(SPo_bull: Decimal, SPo_bear: Decimal, Bn_bull: Decimal, Bn_bear: Decimal, Bn_eth: Decimal) -> Decimal:
    return 1/(((4*SPo_bull*SPo_bear*Bn_bull*Bn_bear)/(Bn_eth**Decimal(2))).sqrt()+1)
