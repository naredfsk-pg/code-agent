# code-agent

Canonical repository for user-owned Agent Skills and custom agents shared between Claude Code and Codex.

## Skills

| Skill | Claude Code | Codex | Purpose |
|---|---|---|---|
| `axon-coordinate` | Compatible | Compatible | Coordinate multi-agent work with ownership, scheduling, evidence-backed handoffs, and durable checkpoints |
| `pdf` | Compatible | Untested | Extract text/tables, fill forms, merge/split, and generate PDFs |

The Claude Code and Codex copies of `axon-coordinate/SKILL.md` were byte-identical when this repository was initialized, so the repository keeps one canonical copy instead of duplicated vendor directories.

`pdf` was vendored in from a bundled Claude skill (its `SKILL.md` still carries a `license: Proprietary` field and a now-missing `LICENSE.txt` reference), which is an intentional exception to the "no vendored bundled skills" rule below — kept because it's in daily use alongside `axon-coordinate`.

## Agents / Personas

The seven AXON Personas are included in both native formats:

```text
agents/claude/*.md   # Claude Code subagents from ~/.claude/agents/
agents/codex/*.toml  # Codex custom agents from ~/.codex/agents/
```

The Codex files are the canonical `.codex/agents` set. The legacy `~/.Codex/agents` mirror is intentionally not duplicated because it is byte-identical and exists only for compatibility.

## Install for Claude Code

Personal installation for all local projects:

```bash
mkdir -p ~/.claude/skills
cp -R skills/axon-coordinate ~/.claude/skills/
```

Project-scoped installation:

```bash
mkdir -p /path/to/project/.claude/skills
cp -R skills/axon-coordinate /path/to/project/.claude/skills/
```

Install the AXON Claude agents globally:

```bash
mkdir -p ~/.claude/agents
cp agents/claude/*.md ~/.claude/agents/
```

Personal installation of `pdf` for all local projects:

```bash
mkdir -p ~/.claude/skills
cp -R skills/pdf ~/.claude/skills/
```

Project-scoped installation:

```bash
mkdir -p /path/to/project/.claude/skills
cp -R skills/pdf /path/to/project/.claude/skills/
```

## Install for Codex

Personal installation matching this AXON configuration:

```bash
mkdir -p ~/.codex/skills
cp -R skills/axon-coordinate ~/.codex/skills/
```

Repository-scoped installation using the shared Agent Skills location:

```bash
mkdir -p /path/to/project/.agents/skills
cp -R skills/axon-coordinate /path/to/project/.agents/skills/
```

Install the AXON Codex agents globally:

```bash
mkdir -p ~/.codex/agents
cp agents/codex/*.toml ~/.codex/agents/
```

Restart the client if a newly created top-level skills directory is not detected in the current session.

## Repository Policy

- Keep one canonical directory per skill under `skills/`.
- Keep Claude and Codex agent definitions under `agents/claude/` and `agents/codex/`.
- Preserve the same seven agent names and domain boundaries across both formats.
- Include a valid `SKILL.md` with only `name` and `description` in its YAML frontmatter.
- Keep optional scripts, references, assets, and agent metadata inside the skill directory.
- Do not vendor bundled system skills, marketplace repositories, plugin caches, histories, sessions, credentials, or machine-specific settings.
- Validate a skill before publishing and review its diff before copying it into a live configuration.

## Current Scope

This repository contains all user-owned Skills currently found in:

- `~/.claude/skills/`
- `~/.codex/skills/`, excluding `.system/`
- `~/.agents/skills/`

It also contains all seven user-owned agent definitions currently found in:

- `~/.claude/agents/`
- `~/.codex/agents/`

Bundled and package-managed Skills are intentionally excluded because they should be installed from their owning product or plugin source.
