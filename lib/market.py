from lib.liquidityPool import LiquidityPool
import lib.log as l
from lib.formula import *
from lib.account import Account
from lib.types import TokenType

eth_price = 4000


class PiSwapMarket(Account):
    def __init__(self):
        super().__init__("Market", 0)
        self.lp = LiquidityPool()
        self.bull_bear_supply = 0
        self.eth_reserve = 0

    def log(f):
        def decorator(self, account, *args, log=True, **kwargs):
            result = f(self, account, *args, **kwargs)
            if (log):
                l.info(self, account)
            return result
        return decorator

    @log
    def mint(self, account, amount):
        supply_after_mint = token_formula(self.eth_reserve + amount)
        tokens_out = supply_after_mint - self.bull_bear_supply
        account.transfer(TokenType.ETH, self, amount)
        self.eth_reserve += amount
        account.mint(TokenType.BULL, tokens_out)
        account.mint(TokenType.BEAR, tokens_out)
        self.bull_bear_supply = supply_after_mint
        return tokens_out

    @log
    def burn(self, account, amount):
        total_eth_after_burn = inverse_token_formula(
            self.bull_bear_supply - amount)
        amount_eth = self.eth_reserve - total_eth_after_burn
        account.burn(TokenType.BULL, amount)
        account.burn(TokenType.BEAR, amount)
        self.transfer(TokenType.ETH, account, amount_eth)
        self.bull_bear_supply -= amount
        self.eth_reserve -= amount_eth
        return amount_eth

    @log
    def initializePool(self, account, amount, amount_bull, amount_bear):
        return self.lp.initialize_pool(account, amount, amount_bull, amount_bear)

    @log
    def addLiquidity(self, account, amount):
        return self.lp.add_liquidity(account, amount)

    @log
    def removeLiquidity(self, account, amount_lt):
        return self.lp.remove_liquidity(account, amount_lt)

    @log
    def swap(self, account, token, buy, amount):
        return self.lp.swap(account, token, buy, amount)
