from lib.account import Account
from lib.formula import *
from lib.types import TokenType


class LiquidityPool(Account):
    def __init__(self):
        super().__init__("Swap", 0)
        self.lt_supply = 0

    def initialize_pool(self, account, amount, amount_bull, amount_bear):
        if self.lt_supply != 0:
            raise Exception("Pool already initialized")

        if amount_bull <= 0 or amount_bear <= 0:
            raise Exception('transfer bull and bear tokens to initialize pool')

        account.transfer(TokenType.BULL, self, amount_bull)
        account.transfer(TokenType.BEAR, self, amount_bear)
        account.transfer(TokenType.ETH, self, amount)
        account.mint(TokenType.LIQUIDITY, amount)
        self.lt_supply += amount
        return amount

    def add_liquidity(self, account, amount):
        if self.lt_supply == 0:
            raise Exception("Pool not initialized yet")

        total_pool_size = self.balances[TokenType.BEAR] + \
            self.balances[TokenType.BULL]
        bull_ratio = self.balances[TokenType.BULL] / total_pool_size

        minted_token_amount = total_pool_size * \
            amount / self.balances[TokenType.ETH]
        liquidity_minted = amount * self.lt_supply / \
            self.balances[TokenType.ETH]
        amount_bull = minted_token_amount * bull_ratio
        amount_bear = minted_token_amount - amount_bull

        account.transfer(TokenType.BULL, self, amount_bull)
        account.transfer(TokenType.BEAR, self, amount_bear)
        account.transfer(TokenType.ETH, self, amount)
        account.mint(TokenType.LIQUIDITY, liquidity_minted)
        self.lt_supply += liquidity_minted
        return liquidity_minted

    def remove_liquidity(self, account, amount_lt):
        liquidity_removed = amount_lt / self.lt_supply

        amount_eth = self.balances[TokenType.ETH] * liquidity_removed
        amount_bull = self.balances[TokenType.BULL] * liquidity_removed
        amount_bear = self.balances[TokenType.BEAR] * liquidity_removed

        account.burn(TokenType.LIQUIDITY, amount_lt)
        self.lt_supply -= amount_lt
        self.transfer(TokenType.ETH, account, amount_eth)
        self.transfer(TokenType.BULL, account, amount_bull)
        self.transfer(TokenType.BEAR, account, amount_bear)
        return amount_eth, amount_bull, amount_bear

    def swap(self, account, tokenIn, tokenOut, amount):
        if tokenIn == TokenType.LIQUIDITY or tokenOut == TokenType.LIQUIDITY:
            raise Exception("Swap does not support liquidity tokens")
        if tokenIn == TokenType.BULL and tokenOut == TokenType.BEAR or tokenIn == TokenType.BEAR and tokenOut == TokenType.BULL:
            raise Exception("Swap does not support bull/bear swap")

        buy = tokenIn == TokenType.ETH
        token = tokenOut if buy else tokenIn
        eth_reserve = self.getEthReserve(token)
        reserveIn = eth_reserve if buy else self.balances[token]
        reserveOut = self.balances[token] if buy else eth_reserve

        invariant = self.balances[token] * eth_reserve
        # new pool sizes
        newReserveIn = reserveIn + amount
        newReserveOut = invariant / newReserveIn

        amountOut = reserveOut - newReserveOut
        account.transfer(tokenIn, self, amount)
        self.transfer(tokenOut, account, amountOut)
        return amountOut

    def getEthReserve(self, tokenType):
        if tokenType == TokenType.LIQUIDITY or tokenType == TokenType.ETH:
            raise Exception("Cannot get reserve for liquidity or eth")

        token_pool_size = self.balances[TokenType.BULL] + \
            self.balances[TokenType.BEAR]
        return (self.balances[TokenType.BEAR if tokenType == TokenType.BULL else TokenType.BULL] / token_pool_size) * self.balances[TokenType.ETH]

    def price_for_1_token(self, tokenType):
        eth_pool = self.getEthReserve(tokenType)
        return (self.balances[tokenType] * eth_pool)/(self.balances[tokenType] - 1) - eth_pool

    def sell_eth_price(self, tokenType, eth_amount):
        invariant = self.balances[tokenType] * \
            self.getEthReserve(tokenType)
        # calculate new pool sizes
        new_eth_pool = self.getEthReserve(tokenType) + eth_amount
        new_token_pool = invariant / new_eth_pool
        # tokens paid out to account
        return self.balances[tokenType] - new_token_pool

    def sell_token_price(self, tokenType, token_amount):
        invariant = self.balances[tokenType] * \
            self.getEthReserve(tokenType)
        # calculate new pool sizes
        new_token_pool = self.balances[tokenType] + token_amount
        new_eth_pool = invariant / new_token_pool
        # eth paid out to account
        return self.getEthReserve(tokenType) - new_eth_pool
