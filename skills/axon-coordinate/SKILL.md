---
name: axon-coordinate
description: Coordinate complex AXON work across multiple agents with explicit ownership, dependency-aware parallel or sequential scheduling, evidence-backed handoffs, and durable checkpoints. Use for multi-agent tasks, work that may span sessions, independent parallel reviews, or tasks at risk of context loss or overlapping edits. Do not use for trivial single-agent work.
---

# AXON Coordinate

Coordinate through the Master. Keep agents flat unless recursive delegation is explicitly required.

## 1. Qualify the Work

Use this workflow only when at least one condition holds:

- two or more specialties are required;
- independent work can run in parallel;
- independent verification materially improves safety;
- work may survive compaction, interruption, or another session;
- shared-file ownership or dependency ordering must be controlled.

Otherwise, use one agent or handle a trivial low-risk task directly.

## 2. Create the Coordination Record

For multi-session or interruption-sensitive work, assign a stable task ID and let only the Master maintain `.axon/tasks/<task-id>.md`. Do not create a record for short, single-session work. Never store credentials or secrets.

Use this minimal format:

```markdown
# <task-id>
Status: planned | in_progress | blocked | completed
Objective:
Acceptance criteria:
Owners:
Dependencies:
Checkpoints:
Evidence:
Risks / decisions:
Next action:
```

Treat the file as durable coordination state, not a transcript. Update it after accepted handoffs and before yielding an incomplete persistent task.

## 3. Build Delegation Packets

Give every agent:

- objective and acceptance criteria;
- bounded scope and explicit file/responsibility ownership;
- relevant context, dependencies, and accepted prior handoffs;
- constraints and permitted side effects;
- expected evidence and the standard handoff envelope;
- notice that the workspace is shared and unrelated edits must not be reverted.

Do not ask two agents to write the same file concurrently.

## 4. Choose Scheduling

Run in parallel when tasks are independent and read-heavy, or when write ownership is disjoint.

Run sequentially when outputs are dependencies, agents would touch the same files, a contract must precede consumers, a bug requires debugger evidence before a fix and QA, or a decision changes downstream scope.

Avoid nested fan-out unless explicitly requested. Prefer the smallest useful agent set.

## 5. Manage Shared State

Before editing or handing off, refresh relevant files and diff/status, preserve user and other-agent changes, stop on overlapping ownership, report stale assumptions, and adapt the plan after each accepted handoff.

Agents return results to the Master; they do not all edit the coordination record.

## 6. Enforce Evidence

Require this envelope:

```markdown
## <Agent> Handoff
**Status**: Completed | Blocked — reason
**Scope / Deliverables**: files, artifacts, or decisions produced
**Evidence**: commands, exit codes, diffs, tests, screenshots, metrics, or citations
**Verification**: PASS | FAIL | N/A — reason for each applicable gate
**Risks / Deferred**: limitations, conflicts, or none
**Recommended Next Step**: owner and concrete action
```

Inspect evidence rather than accepting checkmarks. Return a failed handoff with the exact failed gate. After two unsuccessful correction cycles for the same gate, stop fan-out and surface the blocker and evidence to the user.

## 7. Close or Checkpoint

Complete only when acceptance criteria are met, required evidence is inspected, risks are reported, and no required work remains.

For persistent tasks, update the record with final evidence and status. For incomplete work, record the exact next action, owner, dependency, and blocker so another session can resume without reconstructing the full conversation.

