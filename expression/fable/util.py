from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class IEquatable(Generic[T], ABC):
    @abstractmethod
    def GetHashCode(self) -> int:
        raise NotImplementedError

    def Equals(self, other: T) -> bool:
        raise NotImplementedError


class IComparable(IEquatable[T]):
    def CompareTo(self, other: T) -> int:
        raise NotImplementedError
