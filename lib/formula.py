factor = 1000000
stretch = 100
max_supply = factor


def token_formula(x):
    return -(factor*stretch)/(x+stretch) + factor


def inverse_token_formula(y):
    return (factor*stretch)/(factor-y) - stretch


def price_for_1_token(y):
    return inverse_token_formula(y+1) - inverse_token_formula(y)


def swap_token_formula(x):
    return token_formula(x) * 4
