from decimal import Decimal
from enum import Enum

from lib.types import TokenType


class TxType(Enum):
    MINT = 0
    BURN = 1
    TRANSFER = 2


class Account:
    _log = False

    def __init__(self, name: str, initial_eth_balance: float):
        self.name = name
        self.balances = {
            TokenType.ETH: Decimal(initial_eth_balance),
            TokenType.BULL: Decimal(0),
            TokenType.BEAR: Decimal(0),
            TokenType.LIQUIDITY: Decimal(0)
        }

    def mint(self, type: TokenType, amount: Decimal):
        self.__add(type, amount)
        self.printTx(TxType.MINT, amount, type, None)

    def burn(self, type: TokenType, amount: Decimal):
        self.__sub(type, amount)
        self.printTx(TxType.BURN, amount, type, None)

    def transfer(self, type: TokenType, to, amount: Decimal):
        self.__sub(type, amount)
        to.__add(type, amount)
        self.printTx(TxType.TRANSFER, amount, type, to)

    def __add(self, type: TokenType, amount: Decimal):
        self.balances[type] += amount

    def __sub(self, type: TokenType, amount: Decimal):
        if (amount > self.balances[type]):
            raise Exception(f"insufficient {type} balance")
        self.balances[type] -= amount

    @property
    def log(self):
        return self.__class__._log

    @log.setter
    def log(self, value):
        self.__class__._log = value

    def printTx(self, txType: TxType, amount: Decimal, tokenType: TokenType, to):
        if not self.log:
            return
        if txType == TxType.MINT:
            print(f"MINT: {amount} {tokenType.name} => {self.name}")
        elif txType == TxType.BURN:
            print(f"BURN: {self.name} => {amount} {tokenType.name}")
        elif txType == TxType.TRANSFER:
            print(
                f"TRANSFER: {self.name} {amount} {tokenType.name} => {to.name}")

    def print(self):
        print(
            f'{self.name} balance: {round(self.balances[TokenType.ETH], 2)} ETH  {round(self.balances[TokenType.BULL], 2)} BULL  {round(self.balances[TokenType.BEAR], 2)} BEAR  {round(self.balances[TokenType.LIQUIDITY], 2)} LT')
