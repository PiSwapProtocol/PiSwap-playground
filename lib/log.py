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


def blue(text):
    return '\033[94m' + str(text) + '\033[0m'


def red(text):
    return '\033[91m' + str(text) + '\033[0m'


def bold(text):
    return '\033[1m' + str(text) + '\033[0m'


def info(instance, account):
    print("_________________________________________________\n")
    print(bold(f"Token price"))
    print(
        f'Mint: {blue(price_for_1_token(instance.bull_bear_supply))} {red(price_for_1_token(instance.bull_bear_supply))}')
    if (instance.lp.lt_supply != 0):
        print(
            f'Swap: {blue(instance.lp.price_for_1_token(TokenType.BULL))} {red(instance.lp.price_for_1_token(TokenType.BEAR))}')
    print("_________________________________________________\n")
    if (instance.lp.balances[TokenType.ETH] != 0):
        print(bold(f"Pool sizes"))
        print(
            f'{blue("BULL")}: {round(instance.lp.balances[TokenType.BULL], 5)} tokens & {round(instance.lp.getEthReserve(TokenType.BULL), 5)} ETH')
        print(
            f'{red("BEAR")}: {round(instance.lp.balances[TokenType.BEAR], 5)} tokens & {round(instance.lp.getEthReserve(TokenType.BEAR), 5)} ETH')
        print("_________________________________________________\n")
        amount_buy = 0.001
        print(bold(f"Buying certifictes for {amount_buy} ETH:"))
        print(
            f'{blue("Bull swap")}: Tokens out: {round(instance.lp.sell_eth_price(TokenType.BULL, amount_buy), 5)} Average price: {round(amount_buy/instance.lp.sell_eth_price(TokenType.BULL, amount_buy), 5)} ETH')
        print(
            f'{red("Bear swap")}: Tokens out: {round(instance.lp.sell_eth_price(TokenType.BEAR, amount_buy), 5)} Average price: {round(amount_buy/instance.lp.sell_eth_price(TokenType.BEAR, amount_buy), 5)} ETH')
        print("_________________________________________________\n")
        amount_sell = 1
        print(bold(f"Selling {amount_sell} certifictes:"))
        print(
            f'{blue("Bull swap")}: ETH out: {round(instance.lp.sell_token_price(TokenType.BULL, amount_sell), 5)} Average price: {round(instance.lp.sell_token_price(TokenType.BULL, amount_sell)/amount_sell, 5)} ETH')
        print(
            f'{red("Bear swap")}: ETH out: {round(instance.lp.sell_token_price(TokenType.BEAR, amount_sell), 5)} Average price: {round(instance.lp.sell_token_price(TokenType.BEAR, amount_sell)/amount_sell, 5)} ETH')
        print("_________________________________________________\n")
    if (instance.lp.balances[TokenType.ETH] == 0):
        print("Cannot get NFT price, swap not initialized")
    else:
        print(
            f'NFT Value: {round(instance.lp.balances[TokenType.BEAR] / instance.lp.balances[TokenType.BULL], 2)}ETH')
    print("_________________________________________________\n")
    account.print()
