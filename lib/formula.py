from decimal import Decimal

maxSupply = Decimal(1000000000)
stretchFactor = Decimal(10000)


def token_formula(x: Decimal) -> Decimal:
    return maxSupply - (maxSupply*stretchFactor)/(x+stretchFactor)


def inverse_token_formula(y: Decimal) -> Decimal:
    return (maxSupply*stretchFactor)/(maxSupply-y) - stretchFactor
