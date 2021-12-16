from lib.types import TokenType


class Account:
    def __init__(self, name, initial_eth_balance):
        self.name = name
        self.balances = {
            TokenType.ETH: initial_eth_balance,
            TokenType.BULL: 0,
            TokenType.BEAR: 0,
            TokenType.LIQUIDITY: 0
        }

    def mint(self, type, amount):
        self.__add(type, amount)
        print(f"MINT: {amount} {type.name} => {self.name}")

    def burn(self, type, amount):
        self.__sub(type, amount)
        print(f"BURN: {self.name} => {amount} {type.name}")

    def transfer(self, type, to, amount):
        self.__sub(type, amount)
        to.__add(type, amount)
        print(f"TRANSFER: {self.name} {amount} {type.name} => {to.name}")

    def __add(self, type, amount):
        self.balances[type] += amount

    def __sub(self, type, amount):
        if (amount > self.balances[type]):
            raise Exception(f"insufficient {type} balance")
        self.balances[type] -= amount

    def print(self):
        print(
            f'{self.name} balance: {round(self.balances[TokenType.ETH], 2)}ETH {round(self.balances[TokenType.BULL], 2)}BULL {round(self.balances[TokenType.BEAR], 2)}BEAR {round(self.balances[TokenType.LIQUIDITY], 2)}LT')
