<!-- GSD:project-start source:PROJECT.md -->

## Project

**Vid2Reel**

A personal tool that turns the clips on an iPhone into a finished video from inside a Claude chat on the phone: she attaches clips, answers a few quick questions, and gets back a reel ready to post. It makes two shapes, tall 9:16 for short-form reels and wide 16:9 for longer YouTube videos, and both are first-class. It is a Python and FFmpeg toolbox (`v2r`) in this public repo, fetched into the chat's code sandbox by a small skill, with EDITOR.md as the plain-English handbook the chat's Claude follows. No website, no database, no sign-in, no API.

**Core Value:** A reel worth posting, made entirely from her phone. Everything else can fail; this cannot.

### Constraints

- **Runtime**: Python and FFmpeg only, packages from pip, files from github.com, no other network, no GPU, no paid services, no API keys — it must run in the chat sandbox as it is
- **Size**: at most 30 MiB comes back from a chat (`MAX_RESULT_BYTES` is 24 MiB) — measured, not assumed
- **Time**: any single sandbox command is stopped after 2 minutes — long work runs in the background or in pieces
- **Public repo**: never footage, photos or audio from fixtures/ or work/, never a name, account or secret; no attribution lines in commits — her phone fetches this repo, so it must be public
- **Phone first**: a feature for reels that needs a computer, a second app or a setting she must remember is wrong; the one exception is long YouTube videos, edited on a Mac
- **Two shapes**: tall and wide are one setting, never two programs; every command and test covers both
- **Three jobs**: look measures and decides nothing; the cut list is the only place decisions live and is written by the chat's Claude; render builds exactly the list — a better way of seeing footage later replaces only look
- **Taste**: never in EDITOR.md or the repo; a "Reel style" section per account in its Claude Project
- **Process**: one guide stage is one GSD phase on one branch named for the stage; nothing merges into main until a reel has been made from a phone on that branch

<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->

## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
