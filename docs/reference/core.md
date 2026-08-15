# Core types and helpers

The `expression` package exports the core types used by most applications.

| API | Use it for |
| --- | --- |
| `Option`, `Some`, `Nothing` | A value that may be absent. |
| `Result`, `Ok`, `Error` | An expected success or failure with a reason. |
| `Try`, `Success`, `Failure` | A `Result` whose error is an exception. |
| `pipe`, `compose` | Readable value transformations and reusable workflows. |
| `tagged_union`, `tag`, `case` | Domain alternatives and pattern matching. |
| `curry`, `curry_flip` | Partial application when integrating with curried APIs. |
| `tailrec`, `tailrec_async` | Stack-safe recursive algorithms. |

Use the detailed module pages for all members: {doc}`Option <option>`,
{doc}`Result <result>`, {doc}`Try <try>`, {doc}`Pipe <pipe>`,
{doc}`Compose <compose>`, {doc}`Curry <curry>`, {doc}`Tagged unions <union>`, and
{doc}`Miscellaneous helpers <misc>`.
