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
    print(bold(f"Token price"))
    print(
        f'Mint: {blue(price_for_1_token(m.bull_bear_supply)/2)} {red(price_for_1_token(m.bull_bear_supply)/2)}')
    if (m.lp.lt_supply != 0):
        print(
            f'Swap: {blue(m.lp.spotPrice(TokenType.ETH, TokenType.BULL))} {red(m.lp.spotPrice(TokenType.ETH, TokenType.BEAR))}')
    print("_________________________________________________\n")
    if (m.lp.balances[TokenType.ETH] != 0):
        print(bold(f"Pool sizes"))
        print(
            f'ETH: {m.lp.balances[TokenType.ETH]} tokens / Weight {m.lp.getWeight(TokenType.ETH)}')
        print(
            f'{blue("BULL")}: {m.lp.balances[TokenType.BULL]} tokens / Weight {m.lp.getWeight(TokenType.BULL)}')
        print(
            f'{red("BEAR")}: {m.lp.balances[TokenType.BEAR]} tokens / Weight {m.lp.getWeight(TokenType.BEAR)}')
        print("_________________________________________________\n")
    if (m.lp.balances[TokenType.ETH] == 0):
        print("Cannot get NFT price, swap not initialized")
    else:
        print(
            f'NFT Value: {(m.lp.balances[TokenType.BEAR] / m.lp.balances[TokenType.BULL])} ETH')
    print("_________________________________________________\n")
