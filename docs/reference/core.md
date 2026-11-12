# Core types and helpers

The `expression` package exports the core types used by most applications.

| API | Use it for |
| --- | --- |
| `Option`, `Some`, `Nothing`, `NOTHING` | A value that may be absent; `NOTHING` is the shared empty instance. |
| `Result`, `Ok`, `Error` | An expected success or failure with a reason. |
| `Try`, `Success`, `Failure` | A `Result` whose error is an exception. |
| `pipe`, `compose` | Readable value transformations and reusable workflows. |
| `TaggedUnion`, `case`, `tag` | Explicit case classes, domain alternatives, and pattern matching. |
| `curry`, `curry_flip` | Partial application when integrating with curried APIs. |
| `tailrec`, `tailrec_async` | Stack-safe recursive algorithms. |

Use the detailed module pages for all members: {doc}`Option <option>`,
{doc}`Result <result>`, {doc}`Try <try>`, {doc}`Pipe <pipe>`,
{doc}`Compose <compose>`, {doc}`Curry <curry>`, {doc}`Tagged unions <union>`, and
{doc}`Miscellaneous helpers <misc>`.

## Casting helpers

`upcast(Base, value)` and `downcast(Derived, value)` return the original object
after checking it with `isinstance`; they do not convert it. Incompatible values
raise `TypeError`, including when Python runs with optimization (`-O`).
`try_downcast(Derived, value)` returns `None` for an incompatible value.

The target determines the return type, but the uncurried `upcast` API does not
statically enforce the inheritance relationship. A curried form is planned for
the next major release so the target can be fixed before checking the value.

Targets must support `isinstance`. Parameterized generics such as `list[int]`
and `list[Any]` raise `TypeError` in all three helpers. In particular,
`try_downcast` no longer erases generic arguments and checks only the origin:
that could incorrectly present a list of strings as `list[int]`.
