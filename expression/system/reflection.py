from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Union

Constructor = Callable[..., Any]

EnumCase = Union[str, int]
FieldInfo = Union[str, "TypeInfo"]


@dataclass
class CaseInfo:
    declaringType: TypeInfo
    tag: int
    name: str
    fields: List[FieldInfo]


@dataclass
class TypeInfo:
    fullname: str
    generics: Optional[List[TypeInfo]]
    construct: Optional[Constructor]
    parent: Optional[TypeInfo]
    fields: Optional[Callable[[], List[FieldInfo]]]
    cases: Optional[Callable[[], List[CaseInfo]]]
    enum_cases: Optional[List[EnumCase]]

    def __str__(self) -> str:
        return full_name(self)


def class_type(
    fullname: str,
    generics: Optional[List[TypeInfo]] = None,
    construct: Optional[Constructor] = None,
    parent: Optional[TypeInfo] = None,
) -> TypeInfo:
    return TypeInfo(fullname, generics, construct, parent, None, None, None)


def union_type(
    fullname: str,
    generics: List[TypeInfo],
    construct: Constructor,
    cases: Callable[[], List[List[FieldInfo]]]
) -> TypeInfo:
    def fn():
        caseNames: List[str] = construct.cases()
        return cases().map((fields, i) => CaseInfo(t, i, caseNames[i], fields))

    t: TypeInfo = TypeInfo(fullname, generics, construct, None, None, fn, None)
    return t


def full_name(t: TypeInfo) -> str:
    gen = t.generics if t.generics is not None else []
    if len(gen):
        return t.fullname + "[" + ",".join(map(full_name, gen)) + "]"

    return t.fullname
