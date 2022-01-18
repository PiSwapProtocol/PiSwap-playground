import math
from decimal import Decimal, getcontext

from lib.account import Account
from lib.formula import *
from lib.types import SwapKind, TokenType
from lib.utils import complement

getcontext().prec = 18


class LiquidityPool(Account):
    def __init__(self):
        super().__init__("Swap", 0)
        self.MAX_RATIO = Decimal("0.3")
        self.lt_supply = Decimal(0)
        self.eth_weight = Decimal(1/3)

    def initializePool(self, account: Account, amount: Decimal, amount_bull: Decimal, amount_bear: Decimal) -> Decimal:
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

    def addLiquidity(self, account: Account, amount: Decimal) -> Decimal:
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

    def removeLiquidity(self, account: Account, amount_lt: Decimal) -> Decimal:
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

    def adjustWeights(f):
        def decorator(self, account: Account, tokenIn: TokenType, tokenOut: TokenType, kind: SwapKind, amount: Decimal) -> Decimal:
            buy = True if tokenIn is TokenType.ETH else False
            tradedToken = tokenOut if buy else tokenIn
            price = self.spotPrice(TokenType.ETH, tradedToken.invert())
            balance = self.balances[tradedToken.invert()]

            result = f(self, account, tokenIn, tokenOut, kind, amount)

            if (tokenIn is TokenType.ETH or tokenOut is TokenType.ETH):
                self.eth_weight = 1 / ((2 * balance * price) /
                                       self.balances[TokenType.ETH] + 1)
            return result
        return decorator

    @adjustWeights
    def swap(self, account: Account, tokenIn: TokenType, tokenOut: TokenType, kind: SwapKind, amount: Decimal) -> Decimal:
        if tokenIn == TokenType.LIQUIDITY or tokenOut == TokenType.LIQUIDITY:
            raise Exception("Cannot swap liquidity tokens")
        if tokenIn == tokenOut:
            raise Exception("Cannot swap same token")

        if kind == SwapKind.GIVEN_IN:
            amountOut = self.calcOutGivenIn(tokenIn, tokenOut, amount)
            account.transfer(tokenIn, self, amount)
            self.transfer(tokenOut, account, amountOut)
            return amountOut
        else:
            amountIn = self.calcInGivenOut(tokenIn, tokenOut, amount)
            account.transfer(tokenIn, self, amountIn)
            self.transfer(tokenOut, account, amount)
            return amountIn

    def calcOutGivenIn(self, tokenIn: TokenType, tokenOut: TokenType, amountIn: Decimal) -> Decimal:
        balanceIn = self.balances[tokenIn]
        balanceOut = self.balances[tokenOut]
        weightIn = self.getWeight(tokenIn)
        weightOut = self.getWeight(tokenOut)

        # if (amountIn > balanceIn * self.MAX_RATIO):
        #     raise Exception("MAX_RATIO")

        denominator = balanceIn + amountIn
        base = balanceIn / denominator
        exponent = weightIn / weightOut
        power = base**exponent
        return balanceOut * complement(power)

    def calcInGivenOut(self, tokenIn: TokenType, tokenOut: TokenType, amountOut: Decimal) -> Decimal:
        balanceIn = self.balances[tokenIn]
        balanceOut = self.balances[tokenOut]
        weightIn = self.getWeight(tokenIn)
        weightOut = self.getWeight(tokenOut)

        # if (amountOut > balanceOut * self.MAX_RATIO):
        #     raise Exception("MAX_RATIO")

        base = balanceOut / (balanceOut - amountOut)
        exponent = weightOut / weightIn
        power = base**exponent
        ratio = power - 1

        return balanceIn * ratio

    def spotPrice(self, tokenIn: TokenType, tokenOut: TokenType) -> Decimal:
        if tokenIn == TokenType.LIQUIDITY or tokenOut == TokenType.LIQUIDITY:
            raise Exception("Cannot swap liquidity tokens")

        balanceIn = self.balances[tokenIn]
        balanceOut = self.balances[tokenOut]
        weightIn = self.getWeight(tokenIn)
        weightOut = self.getWeight(tokenOut)
        a = balanceIn / weightIn
        b = balanceOut / weightOut
        return a/b

    def getWeight(self, token: TokenType) -> Decimal:
        if token is TokenType.ETH:
            return self.eth_weight
        else:
            return Decimal((1 - self.eth_weight) / 2)
