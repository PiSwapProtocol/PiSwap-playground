from enum import Enum

class TokenType(Enum):
    ETH = 0
    BULL = 1
    BEAR = 2
    LIQUIDITY = 3

class SwapKind(Enum):
    GIVEN_IN = 0
    GIVEN_OUT = 1

    def invert(self):
        return SwapKind.GIVEN_IN if self == SwapKind.GIVEN_OUT else SwapKind.GIVEN_OUT
