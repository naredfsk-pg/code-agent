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

6. **Mark deliberate simplifications that carry a ceiling**
   - When a simpler implementation is chosen knowingly and it has a real limit — a global lock, an O(n²) scan over data expected to stay small, a naive heuristic — leave a `tradeoff:` comment naming the ceiling and the upgrade path.
   - Example: `# tradeoff: single global lock; move to per-account locks if write throughput becomes a bottleneck`.
   - This applies only to a simplification with a known limit, not to ordinary simple code. A simple implementation with no ceiling needs no comment.

## Implementation Style — Every Language

Write the plainest code that is correct. Obvious and boring beats short and clever. Use an explicit, pragmatic, pipeline-oriented style.

- Favor readability and traceable execution flow over compactness.
- Break complex processing into clear sequential stages.
- Use descriptive intermediate variables for the output of each stage.
- Prefer an explicit loop when the logic contains multiple operations, branching, accumulation, or intermediate state. Reach for the language's compact form only when the transformation is simple and immediately readable.
- Prefer the language's plainest built-in structures — a map and a list — before defining a type to carry data that is only passed through.
- Do not introduce a class hierarchy, interface, generic, or inheritance unless it provides a concrete benefit in the current requirement.
- Use a stateful object for a cohesive service or processing component; use a standalone function for a stateless transformation.
- Extract a private helper only for a distinct processing responsibility; do not create pass-through wrappers.
- Use comments to mark meaningful processing phases when they improve navigation through a longer function.
- Prefer simple control flow over clever language-specific expressions.
- Add defensive checks at boundaries where external or malformed data can reasonably occur.
- Optimize for code that is easy to debug and modify, not for minimum line count.

## Python Coding Style

The implementation style above applies in full. Python-specific points:

- Use comprehensions when the transformation is simple and immediately readable; use an explicit loop otherwise.
- Prefer plain `dict` and `list`. Do not introduce dataclasses, `TypedDict`, protocols, ABCs, or inheritance unless they provide a concrete benefit.
- Avoid clever Python expressions such as nested ternaries, walrus chains, and deep unpacking where a plain statement reads better.
