from decimal import Decimal, getcontext
from typing import Tuple

import lib.log as l
from lib.account import Account
from lib.formula import *
from lib.liquidityPool import LiquidityPool
from lib.types import SwapKind, TokenType
from lib.utils import get_traceback

getcontext().prec = 18

eth_price = 4000


class PiSwapMarket(Account):
    def __init__(self):
        super().__init__("Market", 0)
        self.lp = LiquidityPool()
        self.bull_supply = 0
        self.bear_supply = 0

    def failsafe(f):
        def decorator(self, account: Account, *args, log=True, txLog=None, simulate=False, **kwargs):
            snapshot = self.createSnapshot(account)
            result = None
            try:
                # enable / disable transaction logging
                Account.log = False if txLog is False else (
                    txLog is True or (log and txLog is None))
                result = f(self, account, *args, **kwargs)
                if (log):
                    print()
                    l.info(self)
                if simulate:
                    self.restoreSnapshot(account, snapshot)
            except Exception as e:
                print(get_traceback(e))
                self.restoreSnapshot(account, snapshot)
            return result
        return decorator

    @failsafe
    # def mint(self, account: Account, kind: SwapKind, amount) -> Decimal:
    def mint(self, account: Account, nftValue, amount) -> Tuple[Decimal, Decimal]:
        amount = Decimal(amount)
        nftValue = Decimal(nftValue)
        # amount2 = self.calcMintBurn(True, kind, amount)
        # (amountIn, amountOut) = (
        #     amount, amount2) if kind == SwapKind.GIVEN_IN else (amount2, amount)
        # account.transfer(TokenType.ETH, self, amountIn)
        # self.__mint(account, amountOut)
        # return amount2
        # adjust = 2 * nftValue / (nftValue ** 2 + 1)

        factor = self.__factor(nftValue, amount, account)
        amountBull = amount * factor * nftValue.sqrt()
        amountBear = amount * factor / nftValue.sqrt()

        account.transfer(TokenType.ETH, self, amount)
        account.mint(TokenType.BULL, amountBull)
        self.bull_supply += amountBull
        account.mint(TokenType.BEAR, amountBear)
        self.bear_supply += amountBear

        return amountBull, amountBear

    def __factor(self, nftValue: Decimal, amountIn: Decimal, account: Account) -> Decimal:
        totalEth = self.balances[TokenType.ETH] + amountIn
        balanceBull = account.balances[TokenType.BULL]
        balanceBear = account.balances[TokenType.BEAR]

        a = (amountIn ** 2) * (nftValue + 1/nftValue)
        z = (amountIn + balanceBull * self.spotPrice(TokenType.BULL) +
             balanceBear * self.spotPrice(TokenType.BEAR)) / totalEth
        div = a * (1 - z)
        if (div == 0):
            return Decimal(1)

        b = amountIn * ((balanceBull + self.bull_supply) * nftValue.sqrt() +
                        (balanceBear + self.bear_supply) / nftValue.sqrt())
        c = balanceBull * self.bull_supply + balanceBear * self.bear_supply
        e = 2 * amountIn * (self.bull_supply * nftValue.sqrt() +
                            self.bear_supply / nftValue.sqrt())
        f = self.bull_supply ** 2 + self.bear_supply ** 2

        p = (b - e * z) / div
        q = (c - f * z) / div

        return -p/2 + (p ** 2 / 4 - q).sqrt()

    @failsafe
    # , kind: SwapKind, amount) -> Decimal:
    def burn(self, account: Account, percent) -> Decimal:
        percent = Decimal(percent)
        # amount = Decimal(amount)
        # amount2 = self.calcMintBurn(False, kind, amount)
        # (amountIn, amountOut) = (
        #     amount, amount2) if kind == SwapKind.GIVEN_IN else (amount2, amount)
        # self.__burn(account, amountIn)
        # self.transfer(TokenType.ETH, account, amountOut)
        amountBull = account.balances[TokenType.BULL] * percent
        amountBear = account.balances[TokenType.BEAR] * percent
        bullPrice = self.spotPrice(TokenType.BULL)
        bearPrice = self.spotPrice(TokenType.BEAR)
        amountOut = amountBull * bullPrice + amountBear * bearPrice
        account.burn(TokenType.BULL, amountBull)
        self.bull_supply -= amountBull
        account.burn(TokenType.BEAR, amountBear)
        self.bear_supply -= amountBear
        self.transfer(TokenType.ETH, account, amountOut)
        return amountOut

    @failsafe
    def initializePool(self, account: Account, amount, amount_bull, amount_bear) -> Decimal:
        amount = Decimal(amount)
        amount_bull = Decimal(amount_bull)
        amount_bear = Decimal(amount_bear)
        return self.lp.initializePool(account, amount, amount_bull, amount_bear)

    @failsafe
    def addLiquidity(self, account: Account, amount) -> Decimal:
        amount = Decimal(amount)
        return self.lp.addLiquidity(account, amount)

    @failsafe
    def removeLiquidity(self, account: Account, amount_lt) -> Tuple[Decimal, Decimal, Decimal]:
        amount_lt = Decimal(amount_lt)
        return self.lp.removeLiquidity(account, amount_lt)

    @failsafe
    def swap(self, account: Account, tokenIn: TokenType, tokenOut: TokenType, kind: SwapKind, amount) -> Decimal:
        amount = Decimal(amount)
        return self.lp.swap(account, tokenIn, tokenOut, kind, amount)

    def calcMintBurn(self, mint: bool, kind: SwapKind, amount: Decimal) -> Decimal:
        (kind, amount) = (kind, amount) if mint else (kind.invert(), amount * -1)
        if kind == SwapKind.GIVEN_IN:
            supply_after = token_formula(
                self.balances[TokenType.ETH] + amount)
            amount2 = supply_after - self.bull_bear_supply
        if kind == SwapKind.GIVEN_OUT:
            supply_after = self.bull_bear_supply + amount
            total_eth_after = inverse_token_formula(supply_after)
            amount2 = total_eth_after - self.balances[TokenType.ETH]
        return amount2 if mint else amount2 * -1

    def spotPrice(self, token: TokenType) -> Decimal:
        denominator = self.bull_supply ** 2 + self.bear_supply ** 2
        if (denominator == 0):
            return Decimal(0)
        if (token == TokenType.BULL):
            return self.balances[TokenType.ETH] * self.bull_supply / denominator
        if (token == TokenType.BEAR):
            return self.balances[TokenType.ETH] * self.bear_supply / denominator
        return 0

    def getMaxAmountBurnable(self) -> Decimal:
        '''
        In case of a market exit, users can either burn their bull and bear tokens or swap them.
        Because a certain percentage of the liquidity is locked and cannot be removed it's more profitable
        for users to sell some of the tokens through swapping instead of burning all of them.
        '''
        lockedLiquidity = self.lp.balances[TokenType.LIQUIDITY] / \
            self.lp.lt_supply

        if lockedLiquidity == 0:
            return Decimal(0)
        # get reserves
        (lockedEth, lockedToken) = self.lp.getReserves(
            TokenType.ETH, TokenType.BULL)

        # get amount of locked ETH and tokens
        lockedEth = lockedEth * lockedLiquidity
        lockedToken = lockedToken * lockedLiquidity

        # calculate the amount of tokens to swap to receive the maximum amount of ETH
        amountTokensToSwap = (lockedEth*(lockedToken**2)-maxSupply*lockedEth*lockedToken - stretchFactor*maxSupply*lockedToken + maxSupply * (maxSupply * stretchFactor * lockedEth * lockedToken).sqrt()) / \
            (stretchFactor * maxSupply - lockedEth * lockedToken)

        return lockedToken + amountTokensToSwap

    def nftValue(self) -> Decimal:
        return self.bull_supply / self.bear_supply

    def log(self):
        l.info(self)

    def createSnapshot(self, account: Account):
        return {
            "swap_balance": self.balances.copy(),
            "lp_balance": self.lp.balances.copy(),
            "investor_balance": account.balances.copy(),
            "lt_supply": self.lp.lt_supply,
            "bull_supply": self.bull_supply,
            "bear_supply": self.bear_supply
        }

    def restoreSnapshot(self, account: Account, snapshot):
        self.balances = snapshot["swap_balance"]
        self.lp.balances = snapshot["lp_balance"]
        account.balances = snapshot["investor_balance"]
        self.lp.lt_supply = snapshot["lt_supply"]
        self.bull_supply = snapshot["bull_supply"]
        self.bear_supply = snapshot["bear_supply"]
