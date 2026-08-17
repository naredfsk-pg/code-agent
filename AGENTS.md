# Repository Instructions

## Coding Standards — Highest Implementation Priority

Apply these rules whenever creating or modifying code, services, modules, or tests. Preserve correctness, security, explicit requirements, and necessary performance while applying them.

1. **Readability over cleverness**
   - Prefer explicit, traceable control flow and descriptive names over fancy or compressed expressions.
   - A maintainer should be able to follow the logic without decoding it.
   - Do not trade away meaningful runtime or resource efficiency merely to make code look simpler.

2. **Simplicity and no over-engineering**
   - Implement the smallest design that solves the current requirement.
   - Follow YAGNI. Do not add speculative abstraction layers, patterns, configuration, or extension points.

3. **Top-down function ordering**
   - In a class or module, place the public entry point or first-called function before its implementation details.
   - Place helpers below their caller in call-flow order so the file reads from high-level behavior to low-level details.

4. **No useless wrapper functions**
   - Keep a one- or two-line operation inline when extracting it would only forward arguments or rename another call.
   - Extract such a helper only when the same logic is genuinely reused from multiple call sites.

5. **Strict anti-spaghetti code**
   - Prefer guard clauses and early returns; keep conditional and loop nesting to at most three levels where practical.
   - Do not create god classes or god functions. Split multiple responsibilities into cohesive modules or functions.
   - Keep coupling loose and dependencies explicit so a local change does not cause unrelated breakage.

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
- Extract private helper methods only for a distinct processing responsibility; do not create pass-through wrappers.
- Use comments to mark meaningful processing phases when they improve navigation through a longer function.
- Prefer simple control flow over clever Python expressions.
- Add defensive checks at boundaries where external or malformed data can reasonably occur.
- Optimize for code that is easy to debug and modify, not for minimum line count.
