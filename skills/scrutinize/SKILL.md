---
name: scrutinize
description: Pre-flight scrutiny of requirements, tickets, specs, and plans before any code is written. Questions whether the work should exist at all and whether a simpler approach reaches the same goal, then traces the proposal against the real codebase to expose assumptions that are not true. Trigger on /scrutinize, proactively before starting implementation on any non-trivial request, and whenever the user asks to sanity-check a requirement, ticket, spec, plan, or design. For reviewing code that already exists, use the code_reviewer agent instead.
---

# Scrutinize

Run before work starts. Stand outside the request, ask whether it should exist at all, then ground it against the code that actually exists.

**Scope boundary**: this skill operates on intent — requirements, tickets, specs, plans, designs — and runs before implementation. Judging written code against quality pillars belongs to the `code_reviewer` agent. Diagnosing a runtime failure belongs to `debugger`.

## Operating stance

- **Outsider.** Forget who wrote the request and why they believe it is needed. Read it cold.
- **Grounded, not theoretical.** A plan is only as good as its contact with the existing codebase. Open the real files.
- **Actionable, concise, with rationale.** Every finding states what to change, why, and what evidence led you there. No filler, no restating the request back.

## Workflow

Run in order. Do not skip ahead.

### 1. Intent — what is this actually trying to do?

- State the goal in one sentence, in your own words. If you cannot, the request is underspecified — say so and stop here.
- Separate the stated goal from the underlying need. A requirement usually names a solution; find the problem behind it.
- Then run the ladder against the proposed solution. Stop at the first rung that holds:
  1. **Does this need to exist at all?** A speculative or non-load-bearing need — say so and stop.
  2. **Does it already exist in this codebase?** A helper, type, endpoint, or pattern that already lives here — reuse it. Re-implementing what sits a few files over is the most common waste.
  3. **Does the standard library cover it?** Use it.
  4. **Does a native platform feature cover it?** A DB constraint over application code, CSS over JS, a built-in input type over a picker library.
  5. **Does an already-installed dependency solve it?** Use it. Never add a new dependency for what a few lines can do.
  6. **Can it be one line?** One line.
  7. **Only then**: the minimum that works.
- The ladder does not replace understanding the problem — step 2 still has to run. A smaller change in the wrong place is a second bug, not a simplification.
- Separately from the ladder, ask whether a reduced scope solves 90% of the goal with 10% of the risk, and whether the problem belongs at a different layer (config vs code, build vs runtime).
- If a better alternative exists, name it with rationale. This is the most valuable thing you can output — surface it before anything else.

### 2. Ground — trace the proposal against real code

- Locate every place the proposal would touch the existing system. Open those files. Do not reason from memory or from the request's own description of the code.
- Walk the proposed flow end to end: entry point → call sites → branches → state mutated → exit. Include the code on either side of where the change would land; the seams are where plans break.
- List what the proposal assumes. Mark each assumption `verified at file:line`, `false — <what is actually there>`, or `unverifiable — <what would settle it>`.
- Note every surprise: an unexpected branch, state you did not know existed, a caller nobody mentioned. Surprises are signal.

### 3. Stress — what does the requirement fail to answer?

- **Undefined behavior**: which inputs or states does the requirement simply not specify? Empty, null, huge, unicode, concurrent, retried, partially failed, out of order.
- **Silent consequences**: what would change that nobody asked to change? Performance, error semantics, observability, the contract other callers depend on, on-disk or on-wire format, migration path.
- **Acceptance**: how will anyone know this is done and correct? A requirement with no observable success condition is a finding, not a detail to settle later.
- **Blast radius**: who else depends on what this would touch?

### 4. Report

One tight block per finding, ordered by severity. Use the AXON severity scale so verdicts stay comparable with `code_reviewer`:

- **[CRITICAL]** — the goal is wrong, unachievable as specified, or the approach risks data loss or security exposure
- **[HIGH]** — a false assumption, an unanswered question that blocks correct implementation, or a materially simpler alternative
- **[MEDIUM]** — underspecified edge case, unowned consequence, missing acceptance condition
- **[LOW]** — wording, naming, optional tightening

CRITICAL and HIGH must be resolved before implementation starts.

Per finding: **Finding** — one sentence, cite `file:line` where applicable. **Why it matters** — the consequence, not the principle. **Evidence** — the trace step or assumption that exposed it. **Suggested change** — concrete and minimal.

Close with the standard envelope:

```markdown
## Scrutinize Handoff
**Status**: Completed | Blocked — reason
**Scope / Deliverables**: what was scrutinized, the restated goal, findings by severity
**Evidence**: files opened, assumptions verified or refuted with file:line, alternatives considered
**Verification**: PASS | FAIL | N/A — reason for each applicable gate
**Risks / Deferred**: accepted MEDIUM/LOW findings, unverifiable assumptions, or none
**Recommended Next Step**: proceed as specified / proceed with the named alternative / rework the requirement — and the owning agent
```

## Operating rules

- **No rubber-stamps.** "Looks fine" is not an output. If you genuinely find nothing, state what you opened and what you checked, so the user can judge whether you covered the surface they cared about.
- **Cite or it did not happen.** Every claim about the codebase references a specific file, line, or path. No vague "this might break under load."
- **Distinguish claim from verification.** "The request says X" and "I traced X and confirmed or refuted it" are different — keep them separate in the output.
- **The simpler-alternative pass is mandatory.** Even on a small request, spend one breath asking whether the whole thing is necessary. Skip only if the user explicitly says not to question scope.
- **Lead with structure.** If step 1 or step 2 surfaces a real problem, open with it and drop the nits.
- **No flattery, no hedging.** State the finding.
