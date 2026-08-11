# Repository Instructions

## Python Coding Style

When writing or modifying Python, use an explicit, pragmatic, pipeline-oriented style.

- Favor readability and traceable execution flow over compactness.
- Break complex processing into clear sequential stages.
- Use descriptive intermediate variables for the output of each stage.
- Prefer explicit loops when logic contains multiple operations, branching, accumulation, or intermediate state.
- Use comprehensions when the transformation is simple and immediately readable.
- Use classes for stateful services and cohesive processing components.
- Use standalone functions for simple stateless transformations.
- Prefer straightforward dict and list data structures.
- Do not introduce dataclasses, protocols, abstractions, or inheritance unless they provide a concrete benefit.
- Extract private helper methods when an operation represents a distinct processing responsibility.
- Use comments to mark meaningful processing phases when they improve navigation through a longer function.
- Prefer simple control flow over clever Python expressions.
- Add defensive checks at boundaries where external or malformed data can reasonably occur.
- Optimize for code that is easy to debug and modify, not for minimum line count.
