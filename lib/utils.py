from decimal import Decimal
import traceback


def get_traceback(e):
    lines = traceback.format_exception(type(e), e, e.__traceback__)
    return ''.join(lines)


def complement(a: Decimal) -> Decimal:
    return 1 - a if a < 1 else Decimal(0)
