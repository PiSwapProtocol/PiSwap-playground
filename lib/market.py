from decimal import Decimal, getcontext

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
        self.bull_bear_supply = 0

    def failsafe(f):
        def decorator(self, account: Account, *args, log=True, txLog=None, simulate=False, **kwargs):
            swap_balance = self.balances.copy()
            lp_balance = self.lp.balances.copy()
            investor_balance = account.balances.copy()
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
                    # restore balances
                    self.balances = swap_balance
                    self.lp.balances = lp_balance
                    account.balances = investor_balance
            except Exception as e:
                print(get_traceback(e))
                # restore balances
                self.balances = swap_balance
                self.lp.balances = lp_balance
                account.balances = investor_balance
            return result
        return decorator

    @failsafe
    def mint(self, account: Account, kind: SwapKind, amount) -> Decimal:
        amount = Decimal(amount)
        amount2 = self.calcMintBurn(True, kind, amount)
        (amountIn, amountOut) = (
            amount, amount2) if kind == SwapKind.GIVEN_IN else (amount2, amount)
        account.transfer(TokenType.ETH, self, amountIn)
        self.__mint(account, amountOut)
        return amount2

    @failsafe
    def burn(self, account: Account, kind: SwapKind, amount) -> Decimal:
        amount = Decimal(amount)
        amount2 = self.calcMintBurn(False, kind, amount)
        (amountIn, amountOut) = (
            amount, amount2) if kind == SwapKind.GIVEN_IN else (amount2, amount)
        self.__burn(account, amountIn)
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
    def removeLiquidity(self, account: Account, amount_lt) -> Decimal:
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

    def __mint(self, account: Account, amount: Decimal) -> None:
        account.mint(TokenType.BULL, amount)
        account.mint(TokenType.BEAR, amount)
        self.bull_bear_supply += amount

    def __burn(self, account: Account, amount: Decimal) -> None:
        account.burn(TokenType.BULL, amount)
        account.burn(TokenType.BEAR, amount)
        self.bull_bear_supply -= amount
