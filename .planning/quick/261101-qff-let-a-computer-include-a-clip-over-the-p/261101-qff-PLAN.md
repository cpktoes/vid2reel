---
phase: quick-261101-qff
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - v2r/__main__.py
  - v2r/normalize.py
  - tests/test_normalize.py
  - README.md
  - docs/decisions.md
autonomous: true
requirements: [quick-261101-qff]
commits: none  # the user wants this left UNCOMMITTED on branch stage-17-handbook; the executor makes no git commit at all

estimate:
  tokens: 40000
  raw_tokens: 40000
  tasks: 2
  confidence: low

must_haves:
  truths:
    - "On a computer, `uv run python -m v2r normalize --shape tall|wide --work FOLDER --no-size-limit FILES` converts a file over settings.MAX_ATTACHMENT_BYTES like any other file (status done, its letter kept), in both shapes"
    - "Without the option (the phone's way, and the default), a file over the cap is still left out by size alone before it is opened, with exactly the sentence: '<who> is N MB, over the M MB a phone can reliably send, so it was left out. On a computer the same reel can be made with it included.'"
    - "That sentence never names the option, so the phone's Claude never learns it from a skip"
    - "The cap's number is unchanged (settings.MAX_ATTACHMENT_BYTES, 400 MB) and the option switches off only the size check: the pixel limits, the time allowance and the already-in-the-work-folder check still apply"
    - "README.md explains the option beside the --work paragraph as computer-only; EDITOR.md, skill/, v2r/settings.py, fixtures/ and work/ are untouched"
    - "docs/decisions.md ends with one dated 2026-11-01 Stage 17 line about the option that names no person or account"
    - "The full test suite passes in both shapes and nothing is committed"
  artifacts:
    - path: "v2r/__main__.py"
      provides: "normalize's --no-size-limit option (store_true, default False) passed through as size_limit=not args.no_size_limit"
      contains: "--no-size-limit"
    - path: "v2r/normalize.py"
      provides: "normalize(files, shape, out_dir=None, size_limit=True); convert_one(..., who, size_limit=True) with the check `if size_limit and size_bytes > limit`; the reworded skip sentence"
      contains: "a phone can reliably send, so it was left out"
    - path: "tests/test_normalize.py"
      provides: "the oversized-file test pinned to the new sentence; a size_limit=False test; a CLI test of the option and its default; both shapes"
      contains: "size_limit=False"
    - path: "README.md"
      provides: "one or two plain sentences on --no-size-limit, computer only"
      contains: "--no-size-limit"
    - path: "docs/decisions.md"
      provides: "the dated decision line"
      contains: "2026-11-01 · Stage 17"
  key_links:
    - from: "v2r/__main__.py run() normalize branch"
      to: "v2r/normalize.py normalize()"
      via: "normalize.normalize(args.files, args.shape, args.work, size_limit=not args.no_size_limit)"
      pattern: "size_limit=not args\\.no_size_limit"
    - from: "v2r/normalize.py normalize()"
      to: "convert_one()"
      via: "size_limit passed as the EIGHTH POSITIONAL argument, so the existing test fake convert_one(path, given, number, name, *rest) still forwards it"
      pattern: "convert_one\\(path, as_given, number, name, shape, out_dir, who, size_limit\\)"
    - from: "convert_one() size check"
      to: "settings.MAX_ATTACHMENT_BYTES"
      via: "read at call time; only the check is switched off, the number never moves"
      pattern: "if size_limit and size_bytes > limit"
---

<objective>
Let a computer include a clip that is bigger than the phone's 400 MB cap. `v2r normalize` gets a `--no-size-limit` option (off unless typed); the sentence a skipped big file gets is reworded so it says the file is over what a phone can reliably send and that a computer can make the same reel with it included, without ever naming the option. The option is documented in README.md only.

Purpose: on the Mac, a long or 4K clip over 400 MB can now be used; on the phone nothing changes except the clearer sentence. The phone's Claude must never learn the option, because the cap mirrors what a phone can reliably send and the sandbox is slow on big clips.

Output: the option and the reworded sentence in v2r/__main__.py and v2r/normalize.py, tests for both shapes, two sentences in README.md, one dated line in docs/decisions.md.

HARD RULES for the executor (from the user):
- Make NO git commit of any kind for this task, not per task and not at the end. Leave every change uncommitted on branch stage-17-handbook. This overrides the usual per-task commit in the execute workflow.
- No new dependencies. No attribution lines anywhere.
- Do not touch EDITOR.md (the user writes it, and it must never mention this option), skill/, the numbers in v2r/settings.py, fixtures/ or work/.
- Never run `python -m v2r normalize` from the repo root without `--work FOLDER` pointing into a temporary folder: without it, normalize clears the user's work/ folder.
</objective>

<execution_context>
@$HOME/.claude/gsd-core/workflows/execute-plan.md
@$HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@v2r/__main__.py
@v2r/normalize.py
@tests/test_normalize.py

Facts already gathered (no need to re-read beyond these spots):
- v2r/__main__.py: the normalize parser is lines 26-42 (`--shape`, `files`, `--work`); the dispatch is lines 101-106 and calls `normalize.normalize(args.files, args.shape, args.work)`. Every parser uses allow_abbrev=False; keep it.
- v2r/normalize.py: `convert_one(path, given, number, letter, shape, out_dir, who)` at line 521; its docstring line 524 lists the checks ("found, not already in the work folder, not over the size limit, readable"); the size check is lines 534-540. `normalize(files, shape, out_dir=None)` is at line 657 and calls `convert_one(path, as_given, number, name, shape, out_dir, who)` at line 679.
- v2r/settings.py line 161: `MAX_ATTACHMENT_BYTES = 400 * 1000**2`. Leave the file alone.
- tests/test_normalize.py: imports `main` from v2r.__main__, `normalize` from v2r.normalize, `make_clip` from media; fixture `small_caps`; helpers `convert(clips, shape, out_dir)` (line 71) and `manifest_of(folder)` (line 447). `test_refuse_oversized_file_others_convert` (line 452) sets the cap to 1_000_000, sends a sparse 1_000_001-byte big.mov between two real clips and asserts "limit, so it was left out" at line 466.
- tests/test_normalize.py line 1041 monkeypatches convert_one with a wrapper `convert_one(path, given, number, name, *rest)` that takes NO keyword arguments. That is why normalize() must pass size_limit to convert_one positionally.
- docs/decisions.md lines look like: `- 2026-10-24 · Stage 17 · <what was decided and how it differs>.` (hyphen bullet, ISO date, middle dots).
- README.md line 43 is the paragraph that begins "`normalize`, `look`, `check`, `match` and `render` all take `--work FOLDER`".
</context>

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: End-to-end --no-size-limit, from the command line through normalize to the manifest, with the new skip sentence</name>
  <files>v2r/__main__.py, v2r/normalize.py, tests/test_normalize.py</files>
  <behavior>
    - test_refuse_oversized_file_others_convert (tall and wide, already exists): with the cap at 1_000_000 and big.mov at 1_000_001 bytes, A and C are done and B is skipped, and B's sentence EQUALS "The second file, big.mov, is 1 MB, over the 1 MB a phone can reliably send, so it was left out. On a computer the same reel can be made with it included." It contains neither "size-limit" nor "size_limit". It is still printed. Every other assertion in the test stays.
    - New test_no_size_limit_takes_an_oversized_file (tall and wide, small_caps): cap monkeypatched to 1; one real clip from make_clip (320 by 180). Through the existing convert helper into tmp_path/"capped": the clip is skipped and its sentence contains "a phone can reliably send, so it was left out" and "On a computer". Through normalize([clip], shape, out_dir=tmp_path/"uncapped", size_limit=False): the manifest (read with manifest_of) has finished True, the clip's status is "done", and tmp_path/"uncapped"/"A.mp4" exists.
    - New test_cli_no_size_limit_option_and_its_default (tall and wide, small_caps): this is the parser test. WORK_DIR monkeypatched into tmp_path/"default-work" as a safety net; cap monkeypatched to 1; one real clip. main(["normalize", "--shape", shape, "--work", str(tmp_path/"phone"), str(clip)]) returns 1 and that manifest's clip is skipped (the option defaults to off). main(["normalize", "--shape", shape, "--work", str(tmp_path/"computer"), "--no-size-limit", str(clip)]) returns 0 and that manifest's clip is done (the option parses to on). tmp_path/"default-work" never exists.
  </behavior>
  <action>
Write the two new tests and the changed assertions first (place both new tests directly after test_refuse_oversized_file_others_convert, each with `@pytest.mark.parametrize("shape", ["tall", "wide"])`, because every test covers both shapes) and run them to see them fail. Then:

1. v2r/__main__.py: after normalize's `--work` argument, add `--no-size-limit` with action="store_true" and default=False, help text "include a file over the phone's size cap; for a computer only, never from a phone". In run(), change the normalize call to `normalize.normalize(args.files, args.shape, args.work, size_limit=not args.no_size_limit)`. Nothing else in the file changes.

2. v2r/normalize.py:
   - `normalize(files, shape, out_dir=None, size_limit=True)`; add one docstring sentence saying size_limit=False (the Mac's --no-size-limit) includes a file over settings.MAX_ATTACHMENT_BYTES instead of leaving it out.
   - The call at line 679 becomes `convert_one(path, as_given, number, name, shape, out_dir, who, size_limit)` with size_limit as the eighth POSITIONAL argument, never a keyword: the wrapper in test_manifest_entry_that_cannot_be_written_skips_only_that_file (line 1041) takes `*rest` and no keywords, and a keyword would turn its clips into skipped ones.
   - `convert_one(path, given, number, letter, shape, out_dir, who, size_limit=True)`. Its docstring check list says the size check runs only when size_limit is true, so a computer can switch it off; the other checks always run.
   - The size check becomes `if size_limit and size_bytes > limit:` and keeps its comment that the file is never opened. `limit` stays `settings.MAX_ATTACHMENT_BYTES` read at call time; no number moves into this file.
   - The Refused sentence becomes exactly, as one f-string: `f"{who} is {size_bytes / 1e6:.0f} MB, over the {limit / 1e6:.0f} MB a phone can reliably send, so it was left out. On a computer the same reel can be made with it included."` The old clause after the semicolon, the one promising a way to shrink clips, is deleted entirely. The sentence must not name the option or any command: the phone's Claude reads it, and the user wants the option kept out of the phone's world.
   - No other refusal, check or sentence in the file changes; MAX_VIDEO_SIDE, MAX_PHOTO_PIXELS, the time allowance and the work-folder check all still apply with the size check off.

3. tests/test_normalize.py: in test_refuse_oversized_file_others_convert replace the line-466 assertion with the exact-sentence equality from the behavior list plus the two "not in" checks for "size-limit" and "size_limit"; keep the startswith, "over the ", kind, name, bytes, printed and file-existence assertions. Add the two new tests exactly as the behavior list describes, using make_clip(tmp_path / "in.mp4", 320, 180), monkeypatch.setattr(settings, "MAX_ATTACHMENT_BYTES", 1), the convert and manifest_of helpers, `normalize` (already imported) and `main` (already imported). In the CLI test also monkeypatch.setattr(v2r.normalize, "WORK_DIR", tmp_path / "default-work") before calling main. No new helper, no new import, no new dependency.

Do not commit. Do not run normalize from the repo root without --work.
  </action>
  <verify>
    <automated>uv run pytest -q tests/test_normalize.py -k "oversized or no_size_limit or entry_that_cannot_be_written" && uv run pytest -q tests/test_normalize.py && ! grep -n 'later stage' v2r/normalize.py && grep -n 'if size_limit and size_bytes > limit' v2r/normalize.py && grep -n 'size_limit=not args.no_size_limit' v2r/__main__.py && git diff --quiet -- EDITOR.md skill/ v2r/settings.py</automated>
  </verify>
  <done>
    The selected tests and then the whole of tests/test_normalize.py pass in both shapes; `uv run python -m v2r normalize --help` lists --no-size-limit with its computer-only help text; the skip sentence is exactly the new wording and names no option; test_manifest_entry_that_cannot_be_written_skips_only_that_file still passes unchanged; EDITOR.md, skill/ and v2r/settings.py show no diff; no commit was made.
  </done>
</task>

<task type="auto">
  <name>Task 2: README.md sentence, docs/decisions.md line, and the full test suite</name>
  <files>README.md, docs/decisions.md</files>
  <action>
1. README.md: add a new paragraph directly after the `--work FOLDER` paragraph (line 43), before "## Layout". Write it in the README's plain style, one or two sentences, close to: "`normalize --no-size-limit` includes a file over `MAX_ATTACHMENT_BYTES` (in `v2r/settings.py`) instead of leaving it out. It is for a computer only, never a phone: the cap mirrors what a phone can reliably send and the sandbox is slow on big clips, so EDITOR.md never mentions it." Do not repeat the 400 MB number (it lives in settings.py). Do not change the command table or anything else in README.md.

2. docs/decisions.md: append one line at the very end, in the file's existing style, naming no person and no account: "- 2026-11-01 · Stage 17 · normalize takes `--no-size-limit`, so a computer can include a file over `MAX_ATTACHMENT_BYTES`; the number itself is unchanged. The sentence for a file left out by size now says it is over what a phone can reliably send and that on a computer the same reel can be made with it included, and it no longer promises a way to shrink clips. The option is documented in README.md only, never in EDITOR.md or the skill, so the phone's Claude does not learn it."

3. Run the full suite once (about 2 minutes; macOS has no `timeout`): `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" run-with-timeout 600 -- uv run pytest -q`, with the Bash tool's own timeout raised to 600000 ms or run in the background and waited on. test_editor_handbook.py must still pass, which proves EDITOR.md is untouched and still valid.

4. Confirm nothing was committed: `git status --short` lists exactly the five files of this plan as modified (plus the pre-existing untracked .gsd/ and this quick task's .planning folder), and `git log -1` is still the commit that was HEAD before Task 1.

Do not touch EDITOR.md, skill/, v2r/settings.py, fixtures/ or work/. Do not commit.
  </action>
  <verify>
    <automated>grep -n -- '--no-size-limit' README.md && tail -1 docs/decisions.md | grep -n '^- 2026-11-01 · Stage 17 · ' && git diff --quiet -- EDITOR.md skill/ v2r/settings.py && node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" run-with-timeout 600 -- uv run pytest -q</automated>
    <human-check>On the Mac, with any clip: `uv run python -m v2r normalize --shape tall --work /tmp/v2r-big --no-size-limit CLIP` converts it. A real clip over 400 MB is the true test: without the option it is left out with the new sentence, with it the clip becomes A.mp4. On the phone nothing changes except that sentence; no phone run is needed unless the user wants to see the sentence there.</human-check>
  </verify>
  <done>
    README.md has the computer-only paragraph after the --work paragraph; docs/decisions.md ends with the dated 2026-11-01 Stage 17 line naming no person or account; the full `uv run pytest -q` passes; EDITOR.md, skill/ and v2r/settings.py are unchanged; all five changed files are left uncommitted on stage-17-handbook.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| command line -> normalize | the option and file names come from whoever runs the command: the user on the Mac, or the phone's Claude following EDITOR.md in the sandbox |
| attached file -> FFmpeg/Pillow | a file over the cap is now decoded when the option is on |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-q261101-01 | Denial of service | the phone's Claude using --no-size-limit in the sandbox (2-minute command limit, slow on big clips) | medium | mitigate | the option is off by default; the skip sentence never names it (pinned by an exact-sentence test plus "not in" checks); it is documented in README.md only, never in EDITOR.md or skill/ (Task 1 and Task 2 gate on `git diff --quiet -- EDITOR.md skill/`) |
| T-q261101-02 | Denial of service | decoding a very large file with the size check off | low | mitigate | only the size check is switched off: MAX_VIDEO_SIDE, MAX_PHOTO_PIXELS (decompression-bomb guard) and the per-clip FFmpeg time allowance still apply unchanged |
| T-q261101-03 | Tampering | originals | low | accept | the change adds no write path; the existing already-in-the-work-folder refusal and the never-overwrite rules are untouched |
| T-q261101-04 | Information disclosure | `normalize --help` lists the option | low | accept | the help text itself says computer only, never from a phone; the handbook never asks for --help on normalize |
</threat_model>

<verification>
- `uv run pytest -q tests/test_normalize.py` passes, then the full `uv run pytest -q` passes (run through `gsd-tools run-with-timeout 600`).
- `git diff --quiet -- EDITOR.md skill/ v2r/settings.py` succeeds; nothing in fixtures/ or work/ was touched.
- `git log -1` is unchanged from before execution: no commit was made.

Source coverage (every item of the settled design is planned):
| Source item | Covered by |
|-------------|------------|
| 1. --no-size-limit in __main__.py, passed as size_limit | Task 1 step 1 |
| 2. size_limit through normalize() and convert_one(), check, exact new sentence, docstring | Task 1 step 2 |
| 3. README.md sentences by the --work paragraph; nothing in EDITOR.md or skill/ | Task 2 step 1, gates in both tasks |
| 4. updated oversized test, size_limit=False test, parser test | Task 1 step 3 (the CLI test is the parser test) |
| 5. dated docs/decisions.md line naming no one | Task 2 step 2 |
| No commits, no dependencies, no attribution, hands off EDITOR.md/settings numbers/skill/fixtures/work | objective HARD RULES, both tasks |
</verification>

<success_criteria>
- A file over the cap converts with --no-size-limit and is left out without it, in tall and wide.
- The skip sentence reads exactly "... is N MB, over the M MB a phone can reliably send, so it was left out. On a computer the same reel can be made with it included." and names no option.
- README.md documents the option as computer-only; docs/decisions.md has the dated line.
- The full test suite passes; EDITOR.md, skill/, settings.py's numbers, fixtures/ and work/ are untouched; nothing is committed.
</success_criteria>

<output>
Create `.planning/quick/261101-qff-let-a-computer-include-a-clip-over-the-p/261101-qff-SUMMARY.md` when done, and do NOT commit it either.

In the summary, explain the change in plain English for a non-programmer (per CLAUDE.md):
- On the Mac you can now type `--no-size-limit` after `normalize` to keep a clip bigger than 400 MB instead of having it left out.
- On her phone nothing changes, except that a clip over 400 MB is now left out with the sentence "... over the 400 MB a phone can reliably send, so it was left out. On a computer the same reel can be made with it included." The phone's Claude is never told about the option.
- What to look for: on the Mac, normalize a clip over 400 MB once with and once without the option (always with `--work` pointing at a scratch folder); without it you should read the new sentence, with it you should get A.mp4. Video processing itself did not change, so there is nothing new to watch or listen for in a reel; a phone test is only needed to see the new sentence in the chat.
- The changes are left uncommitted on stage-17-handbook, as asked.
</output>
