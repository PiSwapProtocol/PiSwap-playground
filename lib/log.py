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


def green(text) -> str:
    return '\033[92m' + str(text) + '\033[0m'


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
    bullMint = m.spotPrice(TokenType.BULL)
    bearMint = m.spotPrice(TokenType.BEAR)
    print(
        f'Mint: {blue(bullMint)} {red(bearMint)} | combined {green(bullMint + bearMint)} | NFT Value {bold(bullMint / bearMint)} ETH')
    if (m.lp.lt_supply != 0):
        print(
            f'Swap: {blue(bullPrice)} {red(bearPrice)} | combined {green(bullPrice+bearPrice)}')
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
        lockedPercentage = m.lp.balances[TokenType.LIQUIDITY] / m.lp.lt_supply
        print(
            f'{bold("Amount liquidity held by pool")}: {lockedPercentage * 100} % / {lockedPercentage * totalValue} ETH')

        lockedLiqudityForSwap = inverse_token_formula(m.getMaxAmountBurnable())
        print(f'Locked Liquidity for swap: {lockedLiqudityForSwap} ETH')
        # if lockedLiqudityForSwap > 0:
        #     priceAfterBurn = (
        #         100 + inverse_token_formula(lockedSupply)) ** 2 / 100000000
        #     if bullPrice + bearPrice < priceAfterBurn:
        #         print(
        #             f'{red("NFT Trading halted, locked liquidity can be lowered by arbitrage")}')
        print("_________________________________________________\n")
    if (m.lp.balances[TokenType.ETH] == 0):
        print("Cannot get NFT price, swap not initialized")
    else:
        print(
            f'NFT Value: {format(m.lp.nftValue(), "f")} ETH')
    print("_________________________________________________\n")
