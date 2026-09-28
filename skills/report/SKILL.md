---
name: report
description: Write an evidence-backed report as Markdown and optionally render it to a verified PDF. Two lenses — data science / AI engineering (problem statement, data, results vs baseline, charts, tables, error analysis) and software engineering (process and architecture as Mermaid diagrams, I/O contracts, performance and latency/throughput charts, failure modes) — each with an optional plain-language stakeholder version. Trigger on /report, or when the user asks to write up, summarize, or report an experiment, model evaluation, benchmark, system design, pipeline change, or performance result as a document, .md, or PDF. Not for API reference docs, code comments, or chat-length summaries.
---

# Report

A report exists so a reader can act on results without re-running the work. Every number must survive the question "where did this come from, and compared to what?"

**Scope boundary**: this skill turns work that already exists into a document. Designing or running the experiment or load test belongs to `data_scientist`, `qa_tester`, or `backend`. If the evidence a claim needs does not exist yet, report the gap — never fill it with an estimate dressed as a measurement.

## Workflow

Run in order.

### 1. Choose the lens and the reader

The lens follows the question the reader needs answered:

| Lens | Question it answers | Core sections |
|---|---|---|
| **ds** — data science / AI engineering | Does the model or method solve the problem, by how much against a baseline, and where does it fail? | problem statement · data · method & baseline · results · error analysis · ablation |
| **swe** — software engineering | How does the system work, what goes in and out, how fast is it, and where does it break? | problem statement · process & architecture · I/O contract · performance · failure modes · operations |

Real work often has both sides. For example, a model evaluation also ships a service. Pick the lens that the reader's decision depends on, then borrow single sections from the other lens: a ds report can carry a short serving diagram, and a swe report can carry a model-accuracy table.

The reader is **technical** by default. When non-builders (a manager, a client, ops) also need the result, add a **stakeholder version** written from the same numbers. It uses the same numbers and case IDs as the technical version, with plain vocabulary and less depth.

If the reader or the lens cannot be inferred, ask one question. Write in the user's language; keep identifiers, metric names, file paths, and commands exactly as they are in the source.

Read [references/blueprints.md](references/blueprints.md) for the section skeleton of the chosen lens before writing.

### 2. Write the problem statement first

Both lenses open their body with it. It fixes what "success" means before any result is shown:

- **Context**: the system or process today, in two or three sentences.
- **Problem, with evidence**: what goes wrong, measured ("27% of OCR lines below 0.6 confidence", "p95 latency 5.8 s against a 2 s SLA"). Without a number, it is not yet a problem statement.
- **Goal and success criterion**: the metric and the threshold that would count as solved.
- **Scope and non-goals**: what this work deliberately does not address.

If no success criterion was set before the work started, say so plainly. Do not set one afterwards to fit the result.

### 3. Inventory the evidence

Before writing prose, list every number the report will state and the file it came from: a results file, a CSV, a log, a command's output. Open those files — do not quote from memory or from an earlier summary. A number with no source stays out of the report. An adjusted number keeps its raw value next to it.

For every comparison, record:

- **baseline**: exactly what "before" is (for example, "production as deployed at commit abc123", not "the old one").
- **sample**: size, origin, and whether it also served for tuning.
- **metric**: what it measures, and whether it is a **proxy** (confidence, loss) or **ground truth** (accuracy against labels).
- **conditions**: hardware, versions, config, date. For ds, also data splits and seeds. For swe, also workload profile, concurrency, and warm-up.

### 4. Write top-down

The first screen must stand alone. A reader who stops after it knows the result, what it came from, and how far to trust it.

- **Title + metadata line**: date · audience · data · environment.
- **TL;DR**: 3–6 bullets, each with a number in `baseline → result` form, plus where the gain came from and the most important caveat.
- **Read this first callout** (a Markdown blockquote) whenever a number is easy to misread: a proxy metric, a benchmark profile unlike production, or a comparison that favors one side.
- **Count both directions.** Report "improved 73 / regressed 18 / unchanged 15" alongside the mean, because a mean hides who got hurt.
- **Chart + table + takeaway.** Every chart has the exact values in a table and one sentence saying what to conclude.
- **Failures get equal weight.** Regressions, crashes, and rules that did not help get the same depth as wins.
- **Observed vs inferred.** Label a hypothesis as a hypothesis ("likely", "inferred from behavior").
- **Close with** limitations (their own section), next steps ordered by value against cost, and an appendix of the source paths behind every section.

### 5. Lens-specific rules

**ds — data science / AI engineering**

- **Data** section: source, size, splits, label quality, and leakage checks. State whether the thresholds or hyperparameters were tuned on the same set that is reported.
- **Results table**: the baseline is always a row. Show variance (seeds, CI, or bootstrap) when the gap is small enough that noise could explain it; if there is only one run, say so.
- **Report by slice**, not only in aggregate: per class, per data source, per difficulty. An aggregate gain can hide a slice that got worse.
- **Ablation**: each row adds exactly one change, so the reader sees which step bought what. Name the step that did most of the work, even when it is the unglamorous one.
- **Error analysis with case IDs**: best, worst, and the safety net working. Show input → intermediate → output, the metric before and after, and a short excerpt of the actual output. Use the case block in the blueprints.
- **Offline vs online**: keep offline metrics separate from business or production impact. Do not imply one from the other.

**swe — software engineering**

- **Process**: a Mermaid `flowchart` of the stages, showing which component owns each stage and what data flows along each edge. Add a `sequenceDiagram` when a request crosses services, including retries, fallbacks, and timeouts.
- **I/O contract**: a table per interface — input (format, size limits), output (format, fields), errors (codes and when they occur), and side effects — plus one real request/response example.
- **Performance method first**: hardware, versions, workload profile (and how it matches production), concurrency levels, warm-up excluded, number of runs. A performance number without its method is not reported.
- **Latency**: p50 / p95 / p99, never the mean alone. **Throughput** vs concurrency as a line chart. Show where each system flattens.
- **Where the time goes**: a per-stage breakdown (stacked bar or table), so the bottleneck is visible.
- **Resources**: CPU, GPU, memory, or VRAM at the tested load, when capacity is part of the decision.
- **Relative and absolute**: a speedup needs the absolute number beside it. "1.16× faster" means little until the reader knows the baseline is already 6.2 docs/min.
- **Failure modes and limits**: the concurrency or input size where it crashes or degrades, the error class, whether it reproduces, and what the fallback does.
- **Cross-system comparisons**: state the matched conditions in every table caption. When a published number was measured under a profile unlike production, re-measure at the production profile and lead with that. Mark numbers taken from other sources as transcribed and cite them.

**stakeholder version (either lens)**

- Name each technical step by what it does ("ตัวช่วยดึงขอบกระดาษ", not "U²-Net warp") and use that name consistently.
- No config, paths, or code.
- Put a callout on the first page saying what the metric does and does not mean.
- Use 1–3 headline figures and visual before/after cases instead of ablation depth.
- Add practical guidance for the reader when their behavior affects the result.

### 6. Charts and diagrams

Pick the chart from the shape of the data:

| Data | Chart |
|---|---|
| metric per method or pipeline stage (ablation) | horizontal bar; baseline gray, chosen option highlighted |
| metric vs a parameter (concurrency, threshold, data size) | line with markers, one line per system or variant |
| latency distribution | percentile table + CDF or box plot |
| time per stage | stacked bar |
| training progress | line, train vs validation |
| classification errors | confusion matrix heatmap |
| per-item before vs after | scatter with a y = x line, plus improved/regressed counts |

Chart rules:

- Axis labels include units.
- A truncated y-axis is stated in the caption.
- Each chart makes one point.
- Save PNGs at 150–200 dpi to `reports/figures/`, and reference them with relative paths.
- If labels need Thai, set a Thai-capable font in matplotlib; otherwise keep chart labels in English.

Mermaid diagrams go in fenced ` ```mermaid ` blocks:

- Use `flowchart LR` for pipelines, `sequenceDiagram` for request flows across services, and `stateDiagram-v2` for job or entity lifecycles.
- Keep each diagram under about 12 nodes; split a larger one by stage.
- Label edges with what flows ("JPEG ≤ 1024 px", "PNG mask 320×320").
- Quote any label that contains punctuation: `A["resize (1024 px)"]`. Use `<br/>` for a line break inside a label.
- In a sequence diagram, keep `alt`/`else` conditions and notes to a few words, because long ones wrap mid-word. Keep it to about 10 messages; the PDF caps a diagram's height at 100 mm, so a longer one shrinks until its text is hard to read.

GitHub renders these fences natively, and the PDF script draws them.

### 7. Produce the output

Always write the Markdown first; it is the source of truth.

- Save it where the user asks, or `reports/<topic>-<YYYY-MM-DD>.md` in the project.
- Keep it portable: pipe tables, blockquotes for callouts, standalone images with alt text (the alt text becomes the caption), Mermaid fences. No raw HTML.

**PDF**: render only when the user asks for one.

```bash
python3 <skill-dir>/scripts/render_pdf.py reports/<name>.md            # writes reports/<name>.pdf
python3 <skill-dir>/scripts/render_pdf.py reports/<name>.md -o out.pdf --keep-html
MERMAID_JS=/path/to/mermaid.min.js python3 <skill-dir>/scripts/render_pdf.py ...   # offline machines
```

The script needs `pandoc`, Chrome/Chromium/Edge (or `CHROME_PATH`), and `pdftotext` (poppler). Mermaid is loaded from the jsDelivr CDN unless `MERMAID_JS` points to a local `mermaid.min.js`. The script renders with headless Chrome, then checks two things: every source word and number appears in the PDF's text layer, and every diagram was actually drawn.

Exit codes: `0` verified · `1` text-layer mismatch or diagram failure (do not ship the PDF) · `2` rendered but unverified because `pdftotext` is missing.

### 8. Verify before handing off

- **Numbers**: re-check the TL;DR and every table against the source files. Derived numbers (percentages, "73 / 18 / 15") must add up.
- **PDF**: exit code 0. Then look at every page (Read the PDF). Reject any of these:
  - a mostly empty page mid-report;
  - a callout or a short table split across pages;
  - a clipped image or diagram;
  - chart text too small to read.

  A long table may continue on the next page; its header row repeats.
- **Pairs**: the technical and stakeholder versions state identical numbers and case IDs.

## Anti-patterns seen in real reports

- **Thai text layer broken by WeasyPrint**: the page looks correct, but copy, search, and extraction give "ภำพ" for "ภาพ". This is why the renderer uses Chrome and checks the text layer.
- **Forced page break per section**: leaves pages 70% blank. Let sections flow; only callouts, figures, and diagrams refuse to split.
- **Headline number from an unrepresentative profile**: a 1.6× speedup at 512 input tokens misleads when production prompts run ~3,100 tokens.
- **Mean-only results**: a mean latency or mean accuracy hides the tail and the items that got worse.
- **Success criterion written after the result**: a goal chosen to fit the outcome.
- **Unlabeled proxy**: a confidence score presented as accuracy.
- **Adjusted number without the raw one**: every exclusion (cold start, outlier) shows the raw value and the reason.

## Handoff

```markdown
## Report Handoff
**Status**: Completed | Blocked — reason
**Scope / Deliverables**: report path(s), lens (ds | swe), reader (technical | stakeholder | pair), figures and diagrams produced
**Evidence**: source file for each headline number; render_pdf.py exit code and output
**Verification**: numbers re-checked PASS/FAIL · PDF text layer and diagrams PASS/FAIL/N/A — reason · layout inspected PASS/FAIL/N/A — reason
**Risks / Deferred**: unverified claims, missing ground truth, adjustments made, or none
**Recommended Next Step**: owner and concrete action
```
