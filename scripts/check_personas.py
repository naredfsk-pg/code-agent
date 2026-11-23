#!/usr/bin/env python3
"""Fail when the Claude and Codex persona sets drift apart.

Usage:
    python3 scripts/check_personas.py

The repository policy asks for every persona to carry the coding standards and for each persona to be
edited as a matched .md/.toml pair. Text alone did not enforce either, so this script checks that:
- agents/claude/ and agents/codex/ hold the same persona names
- every persona file has a Coding Standards section
- that section, up to a `---` line or the next heading at its level, is identical within each .md/.toml pair
Exit codes: 0 in sync, 1 drift found.
"""

import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_AGENTS_DIR = REPO_ROOT / "agents" / "claude"
CODEX_AGENTS_DIR = REPO_ROOT / "agents" / "codex"
STANDARDS_HEADING_TEXT = "Coding Standards"
SECTION_END_LINE = "---"


def main():
    claude_names = {path.stem for path in CLAUDE_AGENTS_DIR.glob("*.md")}
    codex_names = {path.stem for path in CODEX_AGENTS_DIR.glob("*.toml")}
    problems = []

    for name in sorted(claude_names - codex_names):
        problems.append(f"{name}: agents/claude/{name}.md has no agents/codex/{name}.toml")
    for name in sorted(codex_names - claude_names):
        problems.append(f"{name}: agents/codex/{name}.toml has no agents/claude/{name}.md")

    # tradeoff: compares the standards within each pair only, because personas deliberately reword the
    # rules for their domain; drift from AGENTS.md wording still needs review, or a per-rule canonical text.
    for name in sorted(claude_names & codex_names):
        claude_text = (CLAUDE_AGENTS_DIR / f"{name}.md").read_text(encoding="utf-8")
        codex_text = read_codex_instructions(CODEX_AGENTS_DIR / f"{name}.toml")
        claude_standards = extract_standards_section(claude_text)
        codex_standards = extract_standards_section(codex_text)

        if claude_standards is None:
            problems.append(f"{name}: agents/claude/{name}.md has no {STANDARDS_HEADING_TEXT} section")
        if codex_standards is None:
            problems.append(f"{name}: agents/codex/{name}.toml has no {STANDARDS_HEADING_TEXT} section")
        if claude_standards is None or codex_standards is None:
            continue

        if claude_standards != codex_standards:
            claude_line, codex_line = first_difference(claude_standards, codex_standards)
            problems.append(
                f"{name}: {STANDARDS_HEADING_TEXT} differs between .md and .toml\n"
                f"    .md:   {claude_line}\n"
                f"    .toml: {codex_line}"
            )

    if problems:
        print(f"persona drift found ({len(problems)}):")
        for problem in problems:
            print(f"  {problem}")
        sys.exit(1)

    persona_count = len(claude_names)
    print(f"ok: {persona_count} persona pairs in sync, {persona_count * 2} files carry the coding standards")


def read_codex_instructions(toml_path):
    try:
        persona = tomllib.loads(toml_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        sys.exit(f"error: {toml_path} is not valid TOML: {error}")
    if "developer_instructions" not in persona:
        sys.exit(f"error: {toml_path} has no developer_instructions")
    return persona["developer_instructions"]


def extract_standards_section(persona_text):
    """Return the Coding Standards lines up to a `---` line or a heading at the same or higher level, or None."""
    lines = persona_text.splitlines()
    start_index = None
    for index, line in enumerate(lines):
        if line.startswith("#") and STANDARDS_HEADING_TEXT in line:
            start_index = index
            break
    if start_index is None:
        return None

    start_level = heading_level(lines[start_index])
    for index in range(start_index + 1, len(lines)):
        line = lines[index]
        if line.strip() == SECTION_END_LINE:
            return lines[start_index:index]
        line_level = heading_level(line)
        if line_level > 0 and line_level <= start_level:
            return lines[start_index:index]
    return lines[start_index:]


def heading_level(line):
    marker = line.split(" ", 1)[0]
    if marker and set(marker) == {"#"}:
        return len(marker)
    return 0


def first_difference(claude_lines, codex_lines):
    for claude_line, codex_line in zip(claude_lines, codex_lines):
        if claude_line != codex_line:
            return claude_line, codex_line

    # One section is a prefix of the other, so the first extra line is the difference.
    shared_length = min(len(claude_lines), len(codex_lines))
    claude_extra = claude_lines[shared_length] if len(claude_lines) > shared_length else "<section ends>"
    codex_extra = codex_lines[shared_length] if len(codex_lines) > shared_length else "<section ends>"
    return claude_extra, codex_extra


if __name__ == "__main__":
    main()
