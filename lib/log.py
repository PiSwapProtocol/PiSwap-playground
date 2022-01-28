from lib.account import Account
from lib.formula import *
from lib.types import TokenType


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[36m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def blue(text) -> str:
    return '\033[94m' + str(text) + '\033[0m'


def red(text) -> str:
    return '\033[91m' + str(text) + '\033[0m'


def bold(text) -> str:
    return '\033[1m' + str(text) + '\033[0m'


def info(m) -> None:
    if m.lp.lt_supply != 0:
        bullPrice = m.lp.spotPrice(TokenType.ETH, TokenType.BULL)
        bearPrice = m.lp.spotPrice(TokenType.ETH, TokenType.BEAR)
        (ethPoolBull, bullPool) = m.lp.getReserves(
            TokenType.ETH, TokenType.BULL)
        (ethPoolBear, bearPool) = m.lp.getReserves(
            TokenType.ETH, TokenType.BEAR)
    print(bold(f"Token price"))
    supply = m.bull_bear_supply
    print(
        f'Mint: {blue(inverse_token_formula(supply)/(supply * 2))} {red(inverse_token_formula(supply)/(supply * 2))}')
    if (m.lp.lt_supply != 0):
        print(f'Swap: {blue(bullPrice)} {red(bearPrice)}')
    print("_________________________________________________\n")
    if (m.lp.lt_supply != 0):
        print(bold(f"Pool sizes"))
        print(f'')
        print(
            f'ETH: {ethPoolBull} ETH / {blue("BULL")}: {bullPool} tokens')
        print(
            f'ETH: {ethPoolBear} ETH / {red("BEAR")}: {bearPool} tokens')
        print("_________________________________________________\n")
        totalValue = bullPrice * bullPool + bearPrice * \
            bearPool + ethPoolBull + ethPoolBear
        print(f'{bold("Amount liquidity held by pool")}: {totalValue} ETH')
        lockedPercentage = m.lp.balances[TokenType.LIQUIDITY] / m.lp.lt_supply
        print(
            f'{bold("Amount liquidity held by pool")}: {lockedPercentage * 100} % / {lockedPercentage * totalValue} ETH')
        print("_________________________________________________\n")
    if (m.lp.balances[TokenType.ETH] == 0):
        print("Cannot get NFT price, swap not initialized")
    else:
        print(
            f'NFT Value: {(m.lp.balances[TokenType.BEAR] / m.lp.balances[TokenType.BULL])} ETH')
    print("_________________________________________________\n")
