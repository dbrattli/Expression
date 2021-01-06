from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from .util import IComparable

# export const symbol = Symbol("numeric");


Numeric = Union[int, "CustomNumeric"]


class CustomNumeric(IComparable[Numeric], ABC):
    @abstractmethod
    def multiply(self, y: Numeric) -> Numeric:
        raise NotImplementedError

    @abstractmethod
    def toPrecision(self, sd: Optional[int] = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def toExponential(self, dp: Optional[int] = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def toFixed(self, dp: Optional[int] = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def toHex(self) -> str:
        raise NotImplementedError


def is_numeric(x: Any) -> bool:
    return isinstance(x, (int, CustomNumeric))


def compare(x: Numeric, y: int) -> int:
    if isinstance(x, int):
        return -1 if x < y else (1 if x > y else 0)
    else:
        return x.CompareTo(y)


def multiply(x: Numeric, y: int) -> Numeric:
    if isinstance(x, int):
        return x * y
    else:
        return x.multiply(y)


def to_fixed(x: Numeric, dp: Optional[int]) -> str:
    if isinstance(x, int) and dp is not None:
        fmt = "{:.%sf}" % dp
        return fmt.format(x)

    return "{}".format(x)


# export function toPrecision(x: Numeric, sd?: number) {
#     if (typeof x === "number") {
#         return x.toPrecision(sd);
#     } else {
#         return x[symbol]().toPrecision(sd);
#     }
# }


# export function toExponential(x: Numeric, dp?: number) {
#     if (typeof x === "number") {
#         return x.toExponential(dp);
#     } else {
#         return x[symbol]().toExponential(dp);
#     }
# }

# export function toHex(x: Numeric) {
#     if (typeof x === "number") {
#         return (Number(x) >>> 0).toString(16);
#     } else {
#         return x[symbol]().toHex();
#     }
# }
