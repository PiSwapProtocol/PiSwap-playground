from decimal import Decimal, getcontext

from lib.account import Account
from lib.formula import *
from lib.types import SwapKind, TokenType

getcontext().prec = 18


class LiquidityPool(Account):
    def __init__(self):
        super().__init__("Swap", 0)
        self.lt_supply = Decimal(0)

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

    def lockLiquidity(f):
        def decorator(self, account: Account, tokenIn: TokenType, tokenOut: TokenType, kind: SwapKind, amount: Decimal) -> Decimal:
            (firstToken, tradedToken) = (
                tokenIn, tokenOut) if tokenIn.value < tokenOut.value else (tokenOut, tokenIn)

            # only adjust weights if first token is ETH, then tradedToken is BULL or BEAR
            if firstToken is TokenType.ETH:
                nonTradedToken = TokenType.BULL if tradedToken is TokenType.BEAR else TokenType.BEAR
                (reserveBefore, _) = self.getReserves(
                    firstToken, nonTradedToken)

            result = f(self, account, tokenIn, tokenOut, kind, amount)

            if (firstToken is TokenType.ETH):
                (reserveAfter, _) = self.getReserves(
                    firstToken, nonTradedToken)
                # half of the liquidity added through the fee is minted to the protocol
                adjustedReserve = reserveBefore + \
                    (reserveAfter - reserveBefore) / 2
                impact = (reserveAfter / adjustedReserve) - 1
                liquidityMinted = self.lt_supply * impact
                self.mint(TokenType.LIQUIDITY, liquidityMinted)
                self.lt_supply += liquidityMinted
            return result
        return decorator

    @lockLiquidity
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
        reserveIn, reserveOut = self.getReserves(tokenIn, tokenOut)
        amountInWithFee = (amountIn * reserveIn) / (amountIn + reserveIn)
        numerator = amountInWithFee * reserveOut
        denominator = reserveIn + amountInWithFee
        return numerator / denominator

    def calcInGivenOut(self, tokenIn: TokenType, tokenOut: TokenType, amountOut: Decimal) -> Decimal:
        reserveIn, reserveOut = self.getReserves(tokenIn, tokenOut)
        numerator = reserveIn * amountOut
        denominator = (reserveOut - amountOut)
        amountWithFee = numerator / denominator
        amountIn = (amountWithFee * reserveIn) / (reserveIn - amountWithFee)
        return amountIn

    def getReserves(self, tokenIn: TokenType, tokenOut: TokenType) -> Decimal:
        reserveIn = self.balances[tokenIn]
        reserveOut = self.balances[tokenOut]
        if (tokenIn == TokenType.ETH):
            ratio = 1 - self.balances[tokenOut] / \
                (self.balances[TokenType.BULL] + self.balances[TokenType.BEAR])
            reserveIn = reserveIn * ratio
        elif (tokenOut == TokenType.ETH):
            ratio = 1 - self.balances[tokenIn] / \
                (self.balances[TokenType.BULL] + self.balances[TokenType.BEAR])
            reserveOut = reserveOut * ratio

        return (reserveIn, reserveOut)

    def spotPrice(self, tokenIn: TokenType, tokenOut: TokenType) -> Decimal:
        if tokenIn == TokenType.LIQUIDITY or tokenOut == TokenType.LIQUIDITY:
            raise Exception("Cannot swap liquidity tokens")
        (reserveIn, reserveOut) = self.getReserves(tokenIn, tokenOut)
        return reserveIn / reserveOut
