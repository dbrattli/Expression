// An explicit short-circuit CE contract. F# has no single universal Result/Option
// builder: Zero and Combine below are choices we can compare with Python.
type ResultBuilder() =
    member _.Return(value) = Ok value
    member _.ReturnFrom(value: Result<'T, 'E>) = value
    member _.Bind(value, continuation) = Result.bind continuation value
    member _.Zero() : Result<unit, 'E> = Ok ()
    member _.Delay(body) = body
    member _.Run(body) = body ()
    member _.Combine(first: Result<unit, 'E>, next) = Result.bind next first

type OptionBuilder() =
    member _.Return(value) = Some value
    member _.ReturnFrom(value: Option<'T>) = value
    member _.Bind(value, continuation) = Option.bind continuation value
    member _.Zero() = None
    member _.Delay(body) = body
    member _.Run(body) = body ()
    member _.Combine(first: Option<unit>, next) = Option.bind next first

let result = ResultBuilder()
let option = OptionBuilder()
let require condition = if not condition then failwith "CE reference assertion failed"

let describe (input: Result<int, string>) = result {
    let! number = input
    let! label = Ok "items"
    return $"{number} {label}"
}
let forward input = result { return! describe input }
require (describe (Ok 3) = Ok "3 items")
require (forward (Error "failed") = Error "failed")

let wrapped: Result<Result<int, string>, string> = result { return Error "inner" }
let delegated: Result<int, string> = result { return! Error "inner" }
require (wrapped = Ok(Error "inner"))
require (delegated = Error "inner")

let trace = ResizeArray<string>()
let stopped: Result<int, string> = result {
    trace.Add "start"
    let! _ = Error "failed"
    trace.Add "unreachable"
    return 42
}
require (stopped = Error "failed")
require (Seq.toList trace = ["start"])

let successfulNone: Option<Option<int>> = option { return None }
let absent: Option<int> = option { return! None }
let conditionalZero: Option<int> = option { if false then return 42 }
require (successfulNone = Some None)
require (absent = None)
require (conditionalZero = None)

let resultZero: Result<unit, string> = result { if false then return () }
require (resultZero = Ok ())

// Return is a builder operation, not a Python-style imperative early return.
let continued: Result<int, string> = result {
    return ()
    trace.Add "after return unit"
    return 43
}
require (continued = Ok 43)
require (Seq.toList trace = ["start"; "after return unit"])
printfn "F# CE reference assertions passed"
