from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field, fields
from typing import Any, TypeVar, dataclass_transform


_T = TypeVar("_T")


@dataclass_transform()
def tagged_union(
    _cls: type[_T] | None = None, *, frozen: bool = False, repr: bool = True, order: bool = False
) -> Callable[[type[_T]], type[_T]] | type[_T]:
    """Tagged union decorator.

    A decorator that turns a dataclass into a tagged union.

    Arguments:
        frozen: Whether the tagged union should be frozen. If True,
            the __setattr__ and __delattr__ methods will be generated.
        repr: If True, the __repr__ method will be generated.
        order: If True, the __lt__ method will be generated. The first
            case will be considered the smallest with index 0 and the
            items will be compared as the tuple (index, value)
    """

    def transform(cls: type[_T]) -> type[_T]:
        cls = dataclass(cls)  # TODO: decide if we should be a dataclass or not
        fields_ = fields(cls)  # type: ignore
        field_names = tuple(f.name for f in fields_)
        original_init = cls.__init__

        def __init__(self: Any, **kwargs: Any) -> None:
            tag = kwargs.pop("tag", None)

            name, value = next(iter(kwargs.items()))
            if name not in field_names:
                raise TypeError(f"Unknown case name: {name}")

            if len(kwargs) != 1:
                raise TypeError(f"One and only one case can be specified. Not {kwargs}")

            match tag or name, name:
                case str(tag), name if tag == name:
                    object.__setattr__(self, "tag", name)
                    object.__setattr__(self, name, value)
                    object.__setattr__(self, "_index", field_names.index(name))
                case tag, name:
                    raise TypeError(f"Tag {tag} does not match case name {name}")

            # Enables the use of dataclasses.asdict
            union_fields = dict((f.name, f) for f in fields_ if f.name in [name, "tag"])
            object.__setattr__(self, "__dataclass_fields__", union_fields)  # type: ignore
            original_init(self)

        def __repr__(self: Any) -> str:
            return f"{cls.__name__}({self.tag}={getattr(self, self.tag)})"

        if order:

            def __lt__(self: Any, other: Any) -> bool:
                if not isinstance(other, cls):
                    return False

                return (self._index, getattr(self, self.tag)) < (other._index, getattr(other, other.tag))  # type: ignore

            cls.__lt__ = __lt__  # type: ignore

        if frozen:

            def __hash__(self: Any) -> int:
                return hash((cls.__name__, self.tag, getattr(self, self.tag)))

            def __setattr__(self: Any, name: str, value: Any) -> None:
                if name in field_names:
                    raise TypeError("Cannot change the value of a tagged union case")
                object.__setattr__(self, name, value)

            def __delattr__(self: Any, name: str) -> None:
                if name in field_names:
                    raise TypeError("Cannot delete a tagged union case")

                object.__delattr__(self, name)

            cls.__setattr__ = __setattr__
            cls.__delattr__ = __delattr__  # type: ignore
            cls.__hash__ = __hash__  # type: ignore

        def __eq__(self: Any, other: Any) -> bool:
            return (
                isinstance(other, cls)
                and self.tag == getattr(other, "tag")
                and getattr(self, self.tag) == getattr(other, self.tag)
            )

        def __copy__(self: Any) -> Any:
            mapping = {self.tag: getattr(self, self.tag)}
            return cls(**mapping)

        def __deepcopy__(self: Any, memo: Any) -> Any:
            value = deepcopy(getattr(self, self.tag), memo)
            mapping = {self.tag: value}
            return cls(**mapping)

        cls.__eq__ = __eq__  # type: ignore
        cls.__init__ = __init__  # type: ignore
        if repr:
            cls.__repr__ = __repr__  # type: ignore
        cls.__match_args__ = field_names  # type: ignore

        # We need to handle copy and deepcopy ourselves because they are needed by Pydantic
        cls.__copy__ = __copy__  # type: ignore
        cls.__deepcopy__ = __deepcopy__  # type: ignore

        return cls

    return transform if _cls is None else transform(_cls)


def case() -> Any:
    """A case in a tagged union."""
    return field(init=False, kw_only=True)


def tag() -> Any:
    """The tag of a tagged union."""
    return field(init=False, kw_only=True)
