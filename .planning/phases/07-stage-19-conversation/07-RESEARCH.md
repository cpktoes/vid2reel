# Phase 7: Stage 19 – Conversation - Research

**Researched:** 2026-11-03
**Domain:** a small command-line tool that edits an existing cut list (JSON), a checker note, one setting block, and a plain-English handbook section
**Confidence:** HIGH for everything about the code (every function named below was opened and read this session); MEDIUM for the handbook word budget (an estimate until the user's draft exists) and for the estimate rule (three data points)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### The brief (from the user's discuss-step prompt; the guide's "Decide: when to ask" is closed)
- **D-01:** The brief is asked **straight away, before looking at the footage**. Four numbered questions in one message, each answerable in a few words and each with a stated default she accepts by skipping it: what the reel is about; which clip or moment is the star; lively or calm (default Lively); shape and length (default tall, about 20 seconds; wide for YouTube). There is no music question: since Stage 18 the clips' own sound is kept unless she says "mute", and a song is added in the posting app. The first two questions are already in EDITOR.md since Stage 17 (05-CONTEXT D-06); this phase folds them into the full brief rather than keeping two rules.
- **D-02:** Any question the message or the chat's Reel style section already answers is left out; "just make it" skips the brief entirely. After looking, at most one further question, and only if the moment she named cannot be found on the sheets. The subject and the star moment decide what Claude looks for on the sheets and what opens the reel.
- **D-03:** Work starts with one line and a time estimate, then silence until the reel. The estimate is a plain rule written in the handbook, drawn from `docs/phone-limits.md` (rows 15 to 18): **about a minute per clip plus three, rounded up**. The reel log (Stage 20) shows whether it drifts.
- **D-04:** The reply is the video; at most two lines on what is in it, naming clips by what is in them and never by letter (no track is named: there is no music); and **three follow-ups chosen from a short fixed menu of what revise can do** (shorter, longer, start with a particular shot, drop a clip, mute it or keep the sound, a wide version), picked by what applies to this reel: "move the frame" only when check noted a crop that keeps little; "keep the sound" only when the sound was muted; "a wide version" only for a tall reel and the reverse. Predictable words, fitted to the reel.
- **D-05:** Errors: Claude quotes the tool's exact sentence (they are already plain English), then adds one sentence on what to do next (fewer clips, attach the clips again, make it shorter). This replaces the handbook's "show the user the error's exact words and stop". When the work folder is gone (the sandbox was wiped between visits), Claude says the clips need attaching again rather than failing confusingly, and may offer the last cut list as text, since a pasted list is saved exactly as pasted and its clips block guards the letters (Stage 16).

### revise: what it does
- **D-06:** `python -m v2r revise` takes an existing cut list (`work/cutlist.json` unless named, `--work FOLDER` on the Mac like the other cut commands) and one named change, and writes **a new numbered file beside the input** (`work/cutlist-2.json`, then `-3`, and so on); the input is never touched. It prints the new path and, in plain English, each field it changed. It never renders. Every output is a new file, and "show me before and after" is two files side by side. — **Reversibility:** reversible.
- **D-07:** **Shorter** (`shorter --to SECONDS --from SHOTS`): the chat's Claude names the shots to take it from, in order, because it has the why notes and the sheets; no weakness score lives in code. revise trims the named shots in that order, each **from its end** (the first frame Claude chose stays, which matters most for the opener) and each down to its recipe floor, before touching any other shot; whatever remains to trim is then shared evenly across the other shots down to their floors. If every shot is at its floor and the reel is still over the target, **whole shots are dropped from the end of Claude's named list** until the target is met, each one printed, and never the first shot. revise never goes under the floor. The guide's check after "shorter" (the same shots, just less of them) is met.
- **D-08:** **Longer** (`longer --to SECONDS --from SHOTS`): the mirror. Claude names the shots that can run on; revise extends each at its end inside its clip's working length, up to the recipe ceiling (a photo's own length is its ceiling), in order. If the target still cannot be reached, revise says how far it got and the rest is a new moment for Claude to add by editing the list itself.
- **D-09:** **Reorder** (`reorder 3,1,2,4`, a full list of shot numbers): "start with a particular shot" is a reorder. **Drop** (`drop C` by clip letter removes every shot of that clip; `drop shot 3` removes one shot). Whether the dropped clip's record stays in the `clips` block is decided by what check already requires (research confirms); the cover, when it pointed at a dropped or moved shot, is re-pointed to the same shot's new number on a reorder and cleared to the default first frame on a drop, and revise says so.
- **D-10:** **Sound** (`sound keep` or `sound off`, with `--shot N` for one shot): every shot by default, one shot when named.
- **D-11:** **Canvas** (`canvas wide` or `canvas tall`): rewrites width and height only; fps, shots, focus points and everything else stay. The handbook gives the order for "a wide version": normalize wide first, then revise, then check, match and render; check already refuses a wide list over tall working copies (Stage 16 D-03), so nothing silently renders wrong.
- **D-12:** Shots are named **by number in list order from 1**, as the cover already does; clips **by letter**. Letters and numbers never reach her: Claude translates to "the one where the dog runs in". revise refuses, with one sentence, a shot number or letter the list does not have.
- **D-13:** Each revision changes only its own fields, and **tests prove it**: for every change, every field the change does not name (why notes, focus points, moves, touch-up numbers, fades, loudness, version, cover unless D-09 applies) is identical before and after, and the change itself is exactly as asked (target length met to the frame, order as given, shots gone, sound set, canvas set). Times revise writes round to whole frames by the Stage 16 rule.

### Recipe floors
- **D-14:** The cut list gains an optional top-level **`recipe`** field: `"lively"` or `"calm"`. The list stays version 1. check validates the value; render ignores it; revise reads it. A list without it (older lists, pasted lists) is treated as **Lively, the default**, and check notes that it assumed it. — **Reversibility:** costly — the field enters the schema and the handbook's example lists; removing it later means editing every example and test list.
- **D-15:** Floors and ceilings in **settings.py**, taken from the handbook as it stands: Lively 1.5 to 3 seconds, Calm 3 to 5 seconds. A test in `tests/test_editor_handbook.py` keeps EDITOR.md's recipe sentence and those numbers in step, so neither can drift alone.
- **D-16:** check **notes, never refuses**, a shot outside its recipe's range: one sentence naming the shot and the range, like the crop note. A deliberate slow shot later in a reel, which the handbook allows, still renders. A photo shot is exempt from the ceiling (it runs up to its own four seconds, `PHOTO_SECONDS`); the floor still applies.

### The handbook
- **D-17:** EDITOR.md gains a section called **"Talking with her"** covering D-01 to D-05 and the follow-up menu with, for each follow-up, the revise call and exactly which fields change. The words are the user's: a draft is written to this phase folder for him to approve or edit (as Stage 17's D-08), and EDITOR.md changes only as his text. The draft folds in what the handbook now says twice (the two-question rule in "Before editing", the sending lines, the error line) and adds the guide's watch-out that a new set of clips deserves a fresh chat. **Room:** draft first and tighten; the cap (`MAX_WORDS`, 1,500) rises to 1,800 only if the tightened whole still will not fit, with a decisions line saying why.
- **D-18:** The handbook never names `--work`, `--no-size-limit` or any Mac-only switch (the existing guard tests stay), and every command it names must exist in `v2r`'s command line (the existing guard extends to `revise`).

### Records and the phone test
- **D-19:** REQUIREMENTS.md's CONV-01, CONV-04, CONV-05 and CONV-07 still speak of music ("music" in the brief, "which track" in the reply, "change the music or sound", "different song"); they are reworded in this phase's first plan to match Stage 18: no music question, no track in the reply, "keep or mute the sound", and "mute it" in the phone test.
- **D-20:** The guide's "Decide: when to ask" is closed with its pick (straight away): a dated line in `docs/decisions.md` and a clause in CLAUDE.md's "Settled so far", written in the first plan.
- **D-21:** The phone test (CONV-07), from the user's phone inside a Project with a Reel style section, on branch `stage-19-conversation`: attach clips, "use branch stage-19-conversation, make a reel", answer the brief, then "shorter", then "mute it", then "a wide version", each changing only what was asked; the user compares the numbered cut lists side by side and times one reel from send to saved for the reel log. Nothing merges before it.

### Claude's Discretion
- Whether revise ends by running the checker on the new list and printing its report (recommended: yes, so the next step is always clear and the handbook need not say "check again").
- The exact spelling of the command grammar, as long as shots are numbers, clips are letters, and each change is one word.
- The `clips` block after `drop C`, per what check requires today.
- The wording of each command's next-step sentence (D-05), and of the "clips again" message.
- How the rehearsals of this stage run (fresh Claude Code sessions on fixture sets, as Stage 17's D-10), and which requests they try: the guide lists nothing but the clips; "make a reel"; "20 seconds, calm, tall"; "just make it"; "wide, for long-form video"; one with a file that is too big.

### Deferred Ideas (OUT OF SCOPE)
- Saved preferences that answer parts of the brief for good, so it shrinks to what changes every time — Stage 21.
- "Taste test" and "update my profile" — Stage 21.
- Cutting to a steady pulse or to a song's beat — Stage 22, which is in question since Stage 18 dropped music from the tool.
- Picking a different moment, a different star or a new shot automatically — never: that is the chat's Claude's judgement, by design.
- A fresh chat suggested for a new set of clips is a handbook line in this phase (D-17), not a feature.
</user_constraints>

<phase_requirements>
## Phase Requirements

The wording of CONV-01, CONV-04, CONV-05 and CONV-07 in `.planning/REQUIREMENTS.md` (lines 71, 74, 75, 77) and success criteria 2, 3 and 5 under Phase 7 in `.planning/ROADMAP.md` still speak of music; CONTEXT D-19 rewords them in the first plan. The table gives what each requirement means after that rewording.

| ID | Description | Research Support |
|----|-------------|------------------|
| CONV-01 | The handbook's "Talking with her" asks a brief of four numbered questions in one message (about; star moment; lively or calm; shape and length), each with a default, leaving out answered ones, skipped on "just make it". No music question. | Handbook budget and the two sentences it replaces (section "The handbook"); rehearsals 1 to 4 and the briefed-versus-"just make it" comparison (Validation Architecture) |
| CONV-02 | At most one further question after looking, only if the named moment cannot be found. | Handbook section; rehearsals |
| CONV-03 | One line with a time estimate at the start, then silence. | Estimate rule evidence from `docs/phone-limits.md` rows 15 to 18 (section "The time estimate") |
| CONV-04 | Reply is the video, at most two lines on what is in it (no track), three follow-ups from the fixed menu; clips named by what is in them. | Follow-up menu with its revise calls and fields changed (section "Follow-up menu"); rehearsals |
| CONV-05 | `python -m v2r revise` applies one named change (shorter or longer to a target, reorder, drop a clip, keep or mute the sound, change the canvas) and leaves every other field untouched; tests prove it. | Mechanics, trimming arithmetic, test approach (sections 1, 2 and 4 below) |
| CONV-06 | Errors are plain English ending with a next step; a gone work folder means asking for the clips again. | Revise refusal sentences plus the handbook sentence; the "work folder gone" rehearsal |
| CONV-07 | Phone test on the branch: attach, brief, reel, "shorter", "mute it", "a wide version", each changing only what was asked. | D-21 script; what to compare (Validation Architecture) |
</phase_requirements>

## Summary

`revise` is a small, pure transform. It reads a list with `check.read_cutlist`, refuses it in one sentence if the list does not satisfy the schema, changes only the fields its change names, writes a new numbered file beside the input, and ends by running `check.check` on the new file and printing `check.report`. Everything it needs already exists: the strict reader, the schema reader, the frame-rounding helper (`plan.frames`, `plan.segment_frames`, `plan.clip_frames`), the sentence habits (`check.shown`, `check.place`) and the checker's report. It never needs FFmpeg, so its tests are fast: the existing 287 tests of `tests/test_cutlist_check.py` and `tests/test_editor_handbook.py` ran in 6.9 seconds this session, and a revise test file built on the same placeholder work folder will cost a few seconds more.

The stage has five traps the planner must plan around, found by reading the code and tests. (1) Chaining: `check`, `match` and `render` default to `work/cutlist.json`, so a second follow-up that forgets to name the newest list silently starts again from the original, which is exactly the guide's Watch-out; revise must print the next commands with the new path, and the handbook must say to use it. (2) `tests/test_render_settings.py` asserts that the set of settings between the `# render:` and `# Phone limits` comments is exactly its list of 34 names, so the new recipe settings must go in their own block outside those lines. (3) Adding an "assumed Lively" note to every list that lacks `recipe` changes the exact note lists in about ten existing tests in `tests/test_cutlist_check.py`; and the approved wide example (a talking head with shots of 10 and 12 seconds) will also trigger the "outside its range" note, so those expectations change too. (4) argparse cannot take an optional positional `[CUTLIST]` in front of a change word (tested this session: `revise drop C` fails with "invalid choice: 'C'"), so the list is named with an option, not a position. (5) `normalize` deletes `manifest.json` and `look.json` (and the working copies) when it runs, so the "a wide version" flow has no `look.json` afterwards; it does not need one, because the touch-up numbers already sit in the list.

The handbook will not fit in 1,500 words with the whole of D-17 in it. The current handbook is 1,309 words; about 65 words are replaced by the new section, leaving 256 words of room. A section that carries the brief, the estimate, the reply, eight follow-ups with their revise calls, the errors and the fresh-chat line is estimated at 350 to 450 words, so the whole is likely 1,550 to 1,700 words. Expect the 1,800 fallback of D-17 unless the user cuts craft words elsewhere; every command written in backticks costs six to nine words because the cap counts each space-separated token.

**Primary recommendation:** Build `v2r/render/revise.py` beside `match.py`, with `revise` as a subcommand with one sub-subcommand per change (`shorter`, `longer`, `reorder`, `drop`, `sound`, `canvas`), each taking `--cutlist PATH` and `--work FOLDER` after the change word; work in whole frames throughout; compare whole before-and-after lists in `tests/test_revise.py`; add `recipe` to the schema and settings in a new settings block; and have revise print the exact next commands naming the new file.

## Architectural Responsibility Map

The usual browser, server and database tiers do not apply; this tool has these owners instead.

| Capability | Primary Owner | Secondary Owner | Rationale |
|------------|---------------|-----------------|-----------|
| Asking the brief, the one-line estimate, the reply and the three follow-ups | `EDITOR.md` (the chat's Claude following the user's words) | the skill, which only fetches the repo and says read EDITOR.md | Conversation and craft live in the handbook (CLAUDE.md: EDITOR.md holds craft and house rules; nothing moves into code or the skill) |
| Choosing which shots to trim or drop, which moment, which star | the chat's Claude, spelled out in `revise`'s arguments | none | D-07: no weakness score lives in code; the cut list is the only place edit decisions live |
| Applying one named change, mechanically, to a cut list | `v2r/render/revise.py` (new) | `check.read_cutlist` and `plan` for reading and rounding | Three jobs that never mix: revise is a transform that decides nothing |
| Saying whether the new list is sound | `v2r/render/check.py` | `schema/cutlist.schema.json` for structure | check already owns problems and notes; revise reuses it and adds one note family (recipe) |
| Shot-length floors and ceilings | `v2r/settings.py` (new block) | EDITOR.md's recipe sentence, tied by a guard test | Every number that controls behaviour lives in settings.py (D-15) |
| Building the reel | `v2r/render` (unchanged) | none | render ignores `recipe`; it builds exactly what the list says |

## Standard Stack

No new library is needed. The edit arithmetic is a few dozen lines of integer maths on frames; no well-maintained open-source library exists for "trim named shots of a JSON list to a target" (it is specific to this list's rules), so nothing is added to `docs/licenses.md`. [ASSUMED: general knowledge; nothing was searched because the work is internal list arithmetic]

### Core (all already in the repo)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python standard library (`json`, `argparse`, `pathlib`, `os`) | 3.13 (Mac via uv; the sandbox reports Python 3.13.16 in the doctor report in `docs/phone-limits.md`) | read, write and name files; the command line | `check.py`, `match.py` and `__main__.py` already use exactly these |
| `jsonschema` | 4.26.0 (pinned in `requirements.txt` and `pyproject.toml`) [VERIFIED: requirements.txt:7 `jsonschema==4.26.0`] | the schema pass `check.schema_problems` uses | revise reuses check's schema pass for the input |
| `pytest` | 9.x (dev dependency) | tests | the whole suite uses it |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Sub-subcommands (`revise shorter ...`) | one flat command with `--change shorter` | Flat is easier to parse but reads worse in the handbook and in the user's mouth; sub-subcommands keep "each change is one word" (CONTEXT Discretion) |
| Positional `[CUTLIST]` before the change word | `--cutlist PATH` after it | The positional form breaks (tested, see section 1.5); the option form works |

**Installation:** none. **Version verification:** no new packages, so no registry check was needed.

## Package Legitimacy Audit

No external package is installed by this phase, so the audit table is empty and the legitimacy check (`gsd-tools query package-legitimacy check`) had nothing to run.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
 the user's phone chat                    the chat's Claude (follows EDITOR.md)
 ───────────────────                      ──────────────────────────────────────
 "shorter" / "mute it" ───────────────▶  picks the change, translates words to numbers
                                          ("the one where the dog runs in" = shot 4)
                                                       │
                                                       ▼
                    python3 -m v2r revise CHANGE ... [--cutlist work/cutlist-N.json]
                                                       │
        ┌──────────────────────────────────────────────┴───────────────────────────────┐
        │ 1 read list strictly (check.read_cutlist)  ──fail──▶ one sentence, exit 1     │
        │ 2 schema pass (check.schema_problems)      ──fail──▶ first sentence, exit 1   │
        │ 3 refuse a bad shot number / letter / target (one sentence each, exit 1)      │
        │ 4 apply ONE change on a deep copy, in whole frames                            │
        │ 5 fix the cover if its shot moved or went (say so)                            │
        │ 6 write work/cutlist-N+1.json (new file, never the input)                     │
        │ 7 print the new path, each changed field in words, then check.report          │
        │ 8 print the next commands naming the new path                                 │
        └───────────────────────────────────────────────────────────────────────────────┘
                                                       │
                                                       ▼
        check work/cutlist-N+1.json  ─▶  render work/cutlist-N+1.json (long command)  ─▶  reel, cover, proof sheets
                                                       │
                                                       ▼
                 Claude sends the video + two lines + three follow-ups chosen from the menu
```

### Recommended Project Structure
```
v2r/render/revise.py        # new: the six changes, the trimming arithmetic, numbering, printing
v2r/render/check.py         # + recipe notes in rule_notes
v2r/render/__init__.py      # + revise in the import line so v2r.render.revise is reachable like render.match
v2r/__main__.py             # + the revise command
v2r/settings.py             # + a "# revise:" block (outside the "# render:" block, see pitfall 2)
schema/cutlist.schema.json  # + optional "recipe"
tests/test_revise.py        # new: whole-list before/after proofs
tests/cutlists.py           # examples gain "recipe": "lively"
tests/test_cutlist_check.py # recipe schema and note tests; exact-note lists updated
tests/test_editor_handbook.py # revise exists; recipe sentence tied to settings (separate tests)
README.md                   # + a revise row in the command table
```

### 1. The mechanics of `revise`, against the code that exists

All line numbers are of the files as read this session (branch `stage-19-conversation`).

**1.1 Reading the list.**
- `check.read_cutlist(path)` is at `v2r/render/check.py:90-114`. It returns `(data, problems)`; `problems` is a list holding one sentence ("There is no cut list at ... yet.", "The cut list is not valid JSON ...", the size, digit and NaN refusals). It refuses a file over `settings.MAX_CUTLIST_BYTES`, a name given twice in one block, NaN and infinity. [VERIFIED: v2r/render/check.py:90-114] revise uses it unchanged and, on a non-empty `problems`, prints `problems[0]` as `v2r revise: ...` to stderr and exits 1, the way `match` does (`v2r/render/match.py:209-213`, `raise MatchError(problems[0])`).
- The schema pass is `check.jsonschema_problem()` (`check.py:135-141`), `check.load_schema()` (`144-149`, raises `check.Refused` with one sentence) and `check.schema_problems(data, schema)` (`288-301`, one sentence per fault in a stable order). Use these on the input and refuse with the first sentence plus "run check to see them all". This is why revise can rely on `segments[i]["from"]` and `["to"]` being numbers and `["sound"]` being "keep" or "off". Do **not** run the whole of `check.check` on the input: its `canvas_problems` (`check.py:366-393`) refuses a tall list over a wide work folder, which is exactly the state the "a wide version" flow starts from.
- `check.time_problems(data)` (`check.py:447-456`) is a pure function of the list and refuses any time over `MAX_CUTLIST_SECONDS` (`settings.py:132`); call it before any frame arithmetic so a 1e300 cannot reach it.
- The manifest is read with `check.read_manifest(work_dir)` (`check.py:117-125`), returning `(manifest, problems)`. `manifest["clips"]` entries have `letter`, `status`, `kind` ("video" or "photo"), `working["seconds"]`. `check.manifest_entry(manifest, letter)` (`396-403`) returns the done entry or None; `check.working_seconds(entry)` (`406-409`) returns the length or None. Only `longer` needs the manifest (to tell a photo from a video); the other five changes can run with the work folder gone, which is useful for the "work folder gone" case. Every other length revise needs is in the list's own `clips` block (`clips[letter]["seconds"]`), which `check.clips_problems` (`491-498`) has already tied to the manifest within a frame.
- `check.segment_lengths(data)` (`567-574`) returns the frames of every segment or None if any is under a frame. revise should use `plan.segment_frames(segment)[1]` itself so it works on a list that has a one-frame shot.

**1.2 Rounding to whole frames (Stage 16 D-01).**
- `plan.frames(seconds, fps=None)` at `v2r/render/plan.py:14-20`: [VERIFIED: v2r/render/plan.py:14-20] docstring `"""Whole frames in `seconds`: the nearest frame, half up (D-01), so 2.5 seconds is 75 frames every time.` and body `return math.floor(round(seconds * fps, 6) + 0.5)`.
- `plan.clip_frames(seconds)` (`plan.py:23-30`) gives a working copy's whole frames with a thousandth-of-a-frame benefit (`settings.CLIP_FRAME_BENEFIT`), so use it, not `frames`, for a clip's length.
- `plan.segment_frames(segment)` at `plan.py:33-35`: [VERIFIED: v2r/render/plan.py:33-35] `return frames(segment["from"]), frames(segment["to"] - segment["from"])`. **The number of frames a shot lasts is the rounded length of `to - from`, not the difference of two rounded ends.** That is the whole trick: to make a shot exactly `n` frames long, leave `from` alone and write `to = from + n / OUTPUT_FPS`. Because `frames(x + n/30) = frames(x) + n` for any whole `n` (half-up rounding commutes with adding a whole number of frames), the result is exactly `n` frames. Round the written value to 3 decimals (an error of at most 0.0005 seconds, 0.015 of a frame) for readable lists, and assert `plan.segment_frames(new)[1] == n` before writing; fall back to 6 decimals if it ever fails. [ASSUMED: the half-up argument above is my own reasoning; a loop test over many off-grid `from` values (see section 4) turns it into a proof]
- `settings.py:13` `OUTPUT_FPS = 30  # frames per second`; `settings.py:139` `MIN_REEL_SECONDS = 3  # seconds: the shortest reel the checker allows`; `settings.py:38` `PHOTO_SECONDS = 4  # seconds a photo's still clip lasts`. [VERIFIED: v2r/settings.py:13,38,139]

**1.3 Naming the new file.**
- `render.new_path(work_dir, shape)` is at `v2r/render/__init__.py:70-78`: [VERIFIED: v2r/render/__init__.py:73-77] `path = Path(work_dir) / f"reel-{shape}-{stamp}.mp4"`, then `n = 2` and `while path.exists() or normalize.part_path(path).exists(): path = ... f"reel-{shape}-{stamp}-{n}.mp4"; n += 1`. The habit is: lowest free number from 2.
- Recommended for revise: the family name is the input's stem with a trailing `-NUMBER` removed (`cutlist-2` becomes `cutlist`); the new number is **one more than the highest existing `STEM-N.json` in the input's folder** (2 if none), so numbers only ever go up even if a middle file was deleted. Revising `cutlist.json` twice gives `cutlist-2.json` then `cutlist-3.json`; revising `cutlist-2.json` gives the next free number, never `cutlist-2-2.json`. Write the whole text to the file with exclusive creation (open mode `"x"`) so two runs can never overwrite each other; this differs from `match.write_whole` (`match.py:189-198`), which writes `NAME.tmp` and `os.replace`s it over the list on purpose because match changes the list in place. Use the same text format as `write_whole`: `json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"`, so a before-and-after diff in a text viewer shows only the changed lines. [VERIFIED: v2r/render/match.py:189-198, same json.dumps arguments]
- `clear_leftovers` in render (`render/__init__.py:52-67`, pattern `LEFTOVER_FILE` at line 43: `^reel-(tall|wide)-\d{8}-\d{6}(-\d+)?(-cover\.part\.jpg|\.part\.mp4)$`) and `normalize.clear_last_job` (`normalize.py:138-160`) never touch `cutlist-N.json`: the first matches only reel and part names; the second deletes only `LAST_JOB_RECORDS = ("manifest.json", "manifest.json.tmp", "look.json", "look.json.tmp")` and lettered media names (`LAST_JOB_FILES = re.compile(r"^[A-Z]{1,3}(-photo)?(\.part)?\.(mp4|jpg)$")`). [VERIFIED: v2r/normalize.py:104-105] So the numbered lists survive both a render and a re-normalize.

**1.4 The `clips` block and `cover`, as check requires them.**
- `check.clips_problems` (`check.py:491-498`) loops over **every** key of the list's `clips` block and compares each with the manifest; it never requires a clip to be used by a shot. `check.look_problems` (`546-564`) refuses a touch-up for a clip that is **not in the clips block** but says nothing about a clip with no shot. `plan.plan` (`plan.py:144` on) loops over segments only. So after `drop C` the clip C record can stay in `clips` (and its touch-up in `look.touch_up`) and the list still passes check, matches the manifest, and renders; leaving both alone also satisfies D-13 ("every field the change does not name is identical"). **Recommendation: `drop C` removes only segments.** The one thing that must not happen is removing a clip from `clips` while its touch-up stays (check would refuse). The schema requires `clips` to hold at least one clip (`"minProperties": 1`) and `segments` at least one item (`"minItems": 1`), so revise must refuse a drop that would leave no shots: "That would leave the reel with no shots, so nothing was changed." [VERIFIED: schema/cutlist.schema.json:25 `"minProperties": 1` and :32 `"minItems": 1`]
- `check.cover_problems` (`check.py:577-596`): the cover is `{"segment": N, "at": SECONDS}`; `segment` must be a whole number from 1 to the number of segments (`The cover names segment N, but the list has only M segments.`), and `at` must be **strictly less** than that segment's length in seconds (`if at >= seconds:` gives `The cover is at X seconds into segment N, but segment N is only Y seconds long.`). [VERIFIED: v2r/render/check.py:586-595] `plan.cover_frame` (`plan.py:129-141`) says in its docstring that the cover "follows its shot when the reel is shortened or reordered", so following the shot is the intended behaviour.
- Recommended cover rules (CONTEXT D-09 is silent on two cases): (a) a **reorder** or a **drop of other shots** that moves the cover's shot: renumber `cover.segment` to the same shot's new number and say so; (b) the cover's shot is **dropped**: delete the `cover` field (default first frame) and say so; (c) `shorter` trims the cover's shot so that `at` is no longer below its new length: delete the `cover` field and say so (the frame the user liked is gone); (d) `longer` and `sound` and `canvas` never touch the cover. If `cover.segment` is not a whole number (check's own refusal, `check.py:583-585`), leave the cover alone and let check report it.

**1.5 The command line (`v2r/__main__.py`).**
- `check` and `render` share one loop at `__main__.py:57-69` that adds a positional `cutlist` (`nargs="?"`, `type=Path`) and `--work` (`type=Path`); `match` repeats it at `70-79`; the dispatch is in `run()` at `127-131` (`check`: `render.check.check(args.cutlist, args.work)`, prints `render.check.report(checked)`, returns 1 if problems) and `141-148` (`match`). Every parser passes `allow_abbrev=False`. [VERIFIED: v2r/__main__.py:57-79,127-148]
- **Tested this session** (a throwaway script outside the repo): with an optional positional `cutlist` before a sub-subparser, `revise drop C` fails with `argument change: invalid choice: 'C' (choose from 'drop')`, because argparse hands "drop" to the optional positional. With a shared parent parser that adds `--cutlist` and `--work` to every change's own parser, all of these parse: `revise shorter --to 12 --from 5,3`, `revise shorter --to 12 --from 5,3 --work w`, `revise reorder 3,1,2,4 --cutlist work/cutlist-2.json`, `revise drop shot 3` and `revise drop C` (with `drop` taking `nargs="+"` and checking its words afterwards: one capital-letter word is a clip, the word `shot` and a whole number is a shot). Give the sub-subparsers `allow_abbrev=False` too. The parent-parser trick means `--work` and `--cutlist` go **after** the change word.
- `from` is a Python keyword, so use `dest="shots"` for `--from`. `type=float` accepts `nan` and `inf`; refuse non-finite targets in one sentence.
- The handbook guard `is_v2r_command` (`tests/test_editor_handbook.py:32-39`) calls `main([name, "--help"])` and wants exit 0; a required sub-subparser still exits 0 on `--help`. [VERIFIED: tests/test_editor_handbook.py:32-39]
- `render/__init__.py:28` imports `from v2r.render import check, match, plan, proof, sound, video`; adding `revise` there makes `render.revise` reachable the way `render.match` is. [VERIFIED: v2r/render/__init__.py:28]

**1.6 Closing the run.** Recommended (CONTEXT Discretion): after writing, call `check.check(new_path, work_dir)` and print `check.report(checked)` (`check.py:781-798`; ends "The cut list is ready to render: N segments, X seconds, tall 1080x1920." or "The cut list has N problems, so nothing can be built until they are fixed."). Then print the next commands with the new path, for example `Next: python3 -m v2r render work/cutlist-2.json`. Exit codes: 1 for a refusal (nothing written); 0 when the file was written and check is clean; 1 when the file was written but check reports a problem (so a chained command does not go on to render). Print the new path **before** the check lines so it is never lost.

### 2. The trimming arithmetic for `shorter` and `longer`

Work in whole frames at 30 a second. Names used below: `L[i]` = frames of shot i now (`plan.segment_frames(seg)[1]`); `FLOOR` and `CEIL` = `plan.frames(` the recipe's seconds `)`, so Lively is 45 and 90 frames and Calm is 90 and 150; compare frames, never seconds, so 3.0 seconds at the ceiling never trips on float noise. The recipe is `data.get("recipe", settings.DEFAULT_RECIPE)`.

**`shorter --to T --from S1,S2,...`**
1. Refuse early, in one sentence each: a shot number outside 1 to N or repeated in `--from`; `T` not a finite number; `TF = plan.frames(T)` below `plan.frames(settings.MIN_REEL_SECONDS)` (90 frames: "A reel must be at least 3 seconds, so it cannot be made shorter than that."); `TF` at or above the reel's current total ("The reel is already X seconds, which is not longer than 12; use longer to go up.").
2. `excess = total - TF`. For every shot, `slack[i] = max(0, L[i] - min(L[i], FLOOR))`. A shot already at or under its floor, and a one-frame shot, has slack 0 and is never changed; print "Shot 4 was already at its shortest, so it was left as it was." for a *named* such shot.
3. **Drops first (decided on floors, so the result is exact):** if the sum of `min(L[i], FLOOR)` over all shots is above `TF`, the reel cannot get down by trimming alone. Drop whole shots from the **end of the named list**, one at a time, never shot 1 and never an unnamed shot, until the sum of floors is at or below `TF`; print each ("Shot 6 was dropped, because every shot was already at its shortest."). If the named list runs out first, see Open Question 3.
4. **Named shots first:** go through the (surviving) named shots in the order given. Each gives `t = min(slack, excess)` frames, taken from its **end** (`to` goes down, `from` never moves), and `excess -= t`. A named shot is taken to its floor before the next one is touched.
5. **Then the others, evenly:** if `excess` is still above 0, share it across the shots that were **not** named and still have slack: repeat { `share, extra = divmod(excess, len(active))`; every active shot gives `min(slack, share)`; the `extra` leftover single frames go one each to the **last** active shots first (this protects the opener; recommended, planner may choose another rule but it must be one fixed rule); drop shots whose slack is spent from `active` } until `excess` is 0 or no slack remains. Every pass either lowers `excess` or removes a shot, so the loop ends.
6. Each changed shot gets `to = round(from + n / OUTPUT_FPS, 3)` for its new frame count `n`. Assert the total of all `plan.segment_frames(seg)[1]` equals `TF` (see next paragraph for the one exception).

Result: the total lands **exactly on `TF`** (not just within a frame), because each shot's frame count is exact and the counts add up. The one exception is the drop case: dropping a whole shot can overshoot, so the reel may end under `TF` by up to one shot's floor (the remaining shots, untrimmed, can add up to less than `TF` only when the shot dropped was long). Say so plainly: "The reel is now 8.5 seconds, 0.5 under the 9 you asked for, because a whole shot had to go." [ASSUMED: this is my reading of D-07's drop rule; Open Question 4 records it]

Worked example for the tests (the approved tall example, `tests/cutlists.py:79-107`): shots are 90, 75, 90, 90, 90, 75, 90 frames (600 total, 20 seconds), Lively floor 45. `shorter --to 15 --from 6,2`: excess 150; shot 6 gives 30 (to 45 frames), shot 2 gives 30 (to 45); excess 90 shared over unnamed shots 1, 3, 4, 5, 7 gives 18 each, so those become 72 frames; total 450 = 15 seconds. The first frame of every shot is unchanged.

**`longer --to T --from S1,S2,...`** (the mirror)
1. Refuse: bad shot numbers; `T` not finite; `TF` at or below the current total ("already X seconds; use shorter").
2. Needs the manifest (for photo or video); if it cannot be read, print check's own sentence and stop. For each named shot compute its **ceiling in frames**: a photo's is its clip's whole frames (`plan.clip_frames(clip seconds)`; the photo is exempt from the recipe ceiling, D-16, and a photo clip is `PHOTO_SECONDS` = 4 seconds long); a video's is `min(CEIL, plan.clip_frames(clip seconds) - plan.frames(from))`, so a shot never runs past the end of its clip. `room[i] = max(0, ceiling - L[i])` (a shot already above the ceiling, such as a 10-second talking-head shot, has room 0 and is never shortened by `longer`).
3. Go through the named shots in order; each gains `min(room, wanted)` frames at its end (`to` goes up), `wanted -= gain`. Round exactly as above.
4. If `wanted` is still above 0, **write the list with what was reached** and say how far it got ("It reached 17.5 seconds of the 20 asked; the rest needs a new moment, which is for Claude to add by editing the list."), exit 0 (D-08).
5. Recommended safety, small: also stop a shot's extension at the first frame of any **later shot of the same clip that starts after this one starts**, so the extension never repeats footage the reel shows next. Handed to the planner (Open Question 6).

**Edge cases, all with one sentence and nothing written unless stated**
- Target below `MIN_REEL_SECONDS` (3 s, 90 frames): refuse (shorter). `longer` below the current total is the "already" refusal.
- A named shot already at its floor: skipped, one line says so; if every named shot is at its floor the unnamed ones still share the excess (step 5), and if nothing can move at all the drops of step 3 apply.
- A photo shot in `shorter`: treated like any shot; the floor applies (D-16: "the floor still applies"). In `longer`: ceiling is the clip's own length.
- A one-frame shot: slack 0 in `shorter` (never dropped unless named, and never the first); in `longer` it may grow like any shot. `plan.plan` makes a one-frame shot the full canvas whatever its move (`plan.py:168-170`, `if count == 1:`), so nothing breaks.
- A target longer than all clips allow: partial write, as above.
- `--from` names every shot: step 5 has no unnamed shots, so only steps 3 and 4 run.
- Off-grid `from` values (for example 1.017): safe by the argument in 1.2; the loop test proves it.

**The other four changes**
- `reorder 3,1,2,4`: the argument must be a permutation of 1 to N (each once); otherwise one sentence ("Reorder needs every shot number once; this list has 7 shots."). Segments are reordered as given; **no segment dict is touched**; the cover is renumbered per rule (a).
- `drop C` removes every segment whose `clip` is C; `drop shot 3` removes segment 3. A letter not in the list's `clips` or with no shot, or a shot number out of range: one sentence. A drop that would leave no shots: refused. A drop that leaves under 3 seconds is written (check will say "The reel is X seconds long; it must be at least 3 seconds."); see Open Question 7. The cover follows rules (a) and (b).
- `sound keep|off [--shot N]`: sets `segments[i]["sound"]` for every shot or for shot N. If nothing would change ("every shot's sound is already off") print that, write nothing, exit 0. Do not touch the top-level `sound` block (D-10; music was closed out of the tool by Stage 18, and the block's fields stay accepted in the schema).
- `canvas tall|wide`: sets `canvas.width` and `canvas.height` from `settings.SHAPES[...]` only; `fps` stays (D-11). If the canvas already has that shape: say so, write nothing. The closing check will print check's own sentence if the work folder was made for the other shape: "The canvas is wide but the clips were normalized for a tall reel; normalize them again with --shape wide to render this list wide." [VERIFIED: v2r/render/check.py:389-392] — which already ends with a next step.

### 3. The `recipe` field, the notes, the settings, the guard

**Schema.** Add to `schema/cutlist.schema.json` `properties` (beside `look`, `sound`; not in `required`; `version` stays `const 1`): `"recipe": {"description": "The recipe the shots were cut to: lively (shots of 1.5 to 3 seconds) or calm (3 to 5). Lively is assumed when left out. render ignores it.", "enum": ["lively", "calm"]}` in the same style as `move`: [VERIFIED: schema/cutlist.schema.json:102-105] `"move": {"description": "...", "enum": ["none", "push-in", "pull-out", "pan-left", "pan-right"]}`. Adding it to `properties` is what stops `check.field_notes` (`check.py:323-358`) from reporting "has a field called "recipe" that v2r does not know". A wrong value is reported by `sentence_enum` (`check.py:230-234`) as `The list's recipe is "fast"; it must be one of lively or calm.` (the path falls to `place`'s last line, `check.py:199`). Do not put numbers in the schema (`tests/test_cutlist_check.py:56-59`, `test_schema_holds_no_settings_numbers`, checks the strings "1080", "1920", "0.92", "1.08", "-14", "0.04"); add a test that the enum equals `set(settings.RECIPES)`.

**Settings.** New block in `v2r/settings.py`, placed between `# doctor` (line 119) and `# render:` (line 122) so it is outside the lines `tests/test_render_settings.py` polices (it reads from the line starting `# render:` to the line starting `# Phone limits` and asserts the assignments there are *exactly* its 34 names, `len(RENDER_SETTINGS) == 34`). [VERIFIED: tests/test_render_settings.py:22-39] Proposed:

```python
# revise: Stage 19's numbers. The recipe floors and ceilings; check notes a shot outside them, nothing refuses.
RECIPES = {  # name: (shortest, longest) shot in seconds
    "lively": (1.5, 3.0),
    "calm": (3.0, 5.0),
}
DEFAULT_RECIPE = "lively"  # the recipe a list is read as when it names none
```

(Names are proposals; the numbers are from EDITOR.md line 25, quoted below.)

**The notes.** They belong in `check.rule_notes` (`check.py:715-732`), which already has `data` and `manifest` and whose docstring states an order ("In this order: the missing touch-up, photos with no move in segment order, crops in letter order, and a reel with no sound at all"). Put the recipe notes first, because they are about the list as a whole, and update that docstring. Existing sentences to match in style: [VERIFIED: v2r/render/check.py:724,728,731] `"There is no touch-up in the list; run match if the clips should match."`, `f"Segment {number}: {shown(segment['clip'])} is a photo with no move."`, `"This reel has no sound at all."`. Proposed new sentences: `"The list names no recipe, so Lively (shots of 1.5 to 3 seconds) was assumed."` and, for a shot outside the range, `"Segment 2 lasts 4.0 seconds; Lively shots last 1.5 to 3."`. Compare in frames (`plan.segment_frames`) against `plan.frames(floor)` and `plan.frames(ceiling)`. A photo (manifest entry `kind == "photo"`) is exempt from the ceiling only (D-16). **Wording choice:** D-16 says "one sentence naming the shot and the range"; the approved wide example has three talking-head shots of 10, 12 and 10 seconds, so a per-shot note would print three near-identical lines on every long-form list. Recommend one grouped sentence per direction ("Segments 1, 3 and 5 last longer than Lively's 3 seconds; segment 7 lasts less than its 1.5."), which still names every shot. Handed to the planner (Open Question 2).

**The handbook guard.** Existing guards in `tests/test_editor_handbook.py` check counts and names, never wording, "so the user can rewrite any sentence" (module docstring, line 1): the word cap `MAX_WORDS = 1500` (line 10), `STEPS`, the regex `NAMED = re.compile(r"python3 -m v2r ([a-z][a-z-]*)")`, `is_v2r_command`, `--work` and `--no-size-limit` absent. [VERIFIED: tests/test_editor_handbook.py:10-15,32-39,67-70] EDITOR.md writes its recipe numbers as **words**: [VERIFIED: EDITOR.md:25] `**Two recipes.** Lively: shots of one and a half to three seconds; the default. Calm: three to five seconds, fewer shots. In both, the first three shots are the shortest in the reel; a slow shot comes later.` So the guard needs a small number reader that accepts digits or the words "one and a half", "one" to "ten" (a dozen lines), finds the sentence beginning "Lively" and the one beginning "Calm", takes the two numbers before "seconds" in each, and asserts they equal `settings.RECIPES`. Make it **separate tests**, not part of `handbook_problems`: many existing tests assert `handbook_problems(steps_text(...)) == []` on tiny texts that have no recipe sentence. Add three separate tests: recipe numbers match settings; `revise` is named in EDITOR.md; the reader itself (fed a text with a wrong number, it complains). `NAMED` already allows `revise` and `is_v2r_command("revise")` will pass once the command exists; `STEPS` should **not** gain `revise` (it is a side road like `join`). `WRONG_SPELLING` is for the six steps only.

### 4. The test approach that proves "only its own fields change"

**Fixtures.** `tests/cutlists.py` already has everything: `placeholder_work(tmp_path, shape)` (lines 33-56) builds a work folder of empty placeholder files and a matching manifest with no FFmpeg; `clips_block(manifest)`; `EXAMPLES[shape](clips)` for the approved tall (7 shots over clips A to E, A to D video, E a photo; cover `{"segment": 4, "at": 1.0}`) and wide (5 shots; a photo C; no cover) lists; `write_list(work, data, name)`. The check tests use the same (`tests/test_cutlist_check.py:774-780`, `context(shape, tmp_path, patch)`), and the checker passes on them without any video file because `look.working_facts` only tests that the named file exists and reads the manifest's numbers (`v2r/look/__init__.py:156-181`). So a revise test is: build, `write_list`, run `main(["revise", ...])` through `v2r.__main__.main` with `capsys`, `json.loads` the new file, compare.

**The comparison helper** (put in the test file, written independently of revise's own printing so it is a real second opinion): `changed_paths(before, after)` walks two parsed lists and returns the set of paths where a value differs or a key is added or removed (list items by index). Each test then asserts the **exact set** of changed paths, which is the strongest form of "only its own fields change":

| Change | What changes (the whole expected set) | What is also asserted |
|--------|----------------------------------------|------------------------|
| `shorter --to 15 --from 6,2` (tall) | only `("segments", i, "to")` for the shots the arithmetic names, plus `("cover",)` when the cover's `at` no longer fits | the sum of `plan.segment_frames` equals `plan.frames(15)`; every `from`, `why`, `focus_*`, `move`, `sound`, `clip`; `clips`; `look`; `sound` block; `canvas`; `version`; `recipe` equal; the named shots hit their floor first; no shot below its floor; unknown fields survive |
| `longer` | only `("segments", i, "to")` for the named shots | no shot above its ceiling or past its clip's end; a photo's ceiling is its own 4 seconds; partial result prints how far it got |
| `reorder` | only `("segments",)` order (as a list of whole dicts) and `("cover", "segment")` when it moves | the multiset of segment dicts is identical; the order is as given; each dict's keys and order unchanged |
| `drop C` / `drop shot N` | only the removed segments and `cover` per rules (a) and (b) | the surviving segments are the original dicts, in order; `clips` and `look.touch_up` untouched; the new list passes `check.check` |
| `sound off` / `sound keep` (`--shot N`) | only `("segments", i, "sound")` | nothing else; the "already" case writes no file |
| `canvas wide` / `canvas tall` | only `("canvas", "width")` and `("canvas", "height")` | `fps`, shots, focus points and everything else equal |

Plus: the input file's bytes are identical after every run; the new file is `cutlist-2.json`, then `cutlist-3.json`; revising `cutlist-2.json` gives `-3` (not `-2-2`); the input's folder holds no other new file; a refusal writes no file and prints one `v2r revise: ...` sentence with exit 1; the printed "changed fields" lines mention exactly the fields in the expected set.

**Add to the fixture before testing:** unknown fields and accepted-but-unbuilt fields (`data["colour"] = "warm"`, `segment["zoom"] = 2`, `data["text"]`, `segment["transition"]`) so "untouched" covers fields revise has never heard of; a segment with an off-grid `from` (such as 1.017); a one-frame shot; a shot at its floor. Run each in both shapes with `@pytest.mark.parametrize("shape", ["tall", "wide"])` as the other test files do (the project rule: "every command and test covers both").

**Property loop for frames.** One test loops `TF` over every frame count from the sum of floors up to the current total (about 500 values for the tall example), runs the pure arithmetic function (so no files, microseconds each) and asserts `sum(frames) == TF` and every shot within `[min(L, FLOOR), L]`. A second loop over off-grid `from` values from 0.000 to 1.000 in steps of 0.001 asserts `plan.segment_frames` of the written shot equals the intended `n`. This is the proof for the rounding argument in 1.2. Keep the arithmetic in a function that takes numbers and returns numbers (no file reading) so the loop is cheap.

**Speed.** No rendering, no FFmpeg, no video. The 287 existing tests in `tests/test_cutlist_check.py` plus `tests/test_editor_handbook.py` ran in 6.9 seconds on this Mac (`uv run pytest ... -q`, 7.5 s wall). A revise file of 80 to 120 tests should add 2 to 4 seconds. [VERIFIED: ran this session]

**Tests that must change** because of `recipe`: in `tests/test_cutlist_check.py`, the helper regex `RULE_NOTE` (lines 74-76) must gain the new notes so the field-note tests still filter them; the exact-note expectations at lines 254-257 (`one_segment... == (0, [], [NO_TOUCH_UP])`), 959-970 (`EXAMPLE_NOTES`, the wide list gains range notes for its 10-, 12- and 10-second shots and the tall list does not), 1021, 1036, 1045-1051, 1063, 1076 and `test_notes_never_refuse` (1091-1108, which lists the exact note order). Easiest: add `"recipe": "lively"` to `tall_example` and `wide_example` in `tests/cutlists.py` (so examples emit no "assumed" note) and update `EXAMPLE_NOTES["wide"]`; the hand-built minimal lists in a few tests (no recipe) then deliberately show the "assumed" note. [VERIFIED: tests/test_cutlist_check.py:74-76,254-257,957-970,1091-1108; tests/cutlists.py:79-107,109-]

### Pattern: one change, one deep copy
```python
# Source: this phase's design, built from v2r/render/check.py and v2r/render/match.py habits
data, problems = check.read_cutlist(path)          # strict reader; problems[0] is the refusal sentence
new = copy.deepcopy(data)                          # change the copy only
# ... apply exactly one change to `new` ...
text = json.dumps(new, indent=2, ensure_ascii=False, allow_nan=False) + "\n"   # match.write_whole's format
with open(next_path, "x", encoding="utf-8") as handle:                         # never overwrites
    handle.write(text)
```

### Anti-Patterns to Avoid
- **Re-deriving the edit:** never call anything that chooses shots; the named list in `--from` is the only judgement (D-07).
- **Counting seconds:** compare and add frames; convert to seconds only when writing `to` and when printing.
- **Rounding both ends:** `frames(to) - frames(from)` is not `plan.segment_frames`; the length is the rounded `to - from`.
- **Rewriting the input:** unlike `match`, revise never replaces its input.
- **Dropping a clip's record while its touch-up stays:** check refuses a touch-up for a clip not in `clips` (`check.py:552-553`).
- **Putting `recipe` numbers in the schema or in render.**

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Strict list reading and its refusal sentences | a new JSON reader | `check.read_cutlist` | it already caps size, digits, NaN and doubled names |
| Schema faults in plain English | new sentences for each fault | `check.schema_problems` | one sentence per keyword is already tested |
| Frame rounding | `round()` or `int()` on seconds | `plan.frames`, `plan.clip_frames`, `plan.segment_frames` | Stage 16 D-01; Python's own `round` is half-to-even and gives different frames |
| Printing text out of the list | `print(segment["why"])` | `check.shown(...)` | strips control characters and caps length (T-4-06); the list is untrusted data |
| The report after a change | a second summary | `check.report(checked)` | one voice, one closing line |
| Atomic new file | temp-and-rename for a new name | open mode `"x"` after building the whole text | cannot overwrite; a half-written file is not possible for text this small |

**Key insight:** the stage's risk is not clever code but small drift: a second way to round frames, a second way to read a list, a second way to say a problem. Reusing check and plan removes all three.

## Runtime State Inventory

Not a rename, refactor or migration phase. Omitted.

## Common Pitfalls

### Pitfall 1: A follow-up that starts from scratch (the guide's Watch-out)
**What goes wrong:** the user says "shorter", then "mute it"; the second revise reads `work/cutlist.json` (the default) and loses the first change. `check`, `match` and `render` default to `work/cutlist.json` too.
**Why it happens:** CONTEXT D-06 fixes the default as `work/cutlist.json`; the new numbered files are not found by default.
**How to avoid:** (a) revise prints the new path and the exact next commands with that path as its last lines; (b) the user's handbook text says every command after a revise names the newest list; (c) the phone test and the rehearsals compare the numbered lists side by side (guide step 4). Option for the planner (Open Question 1): make revise's default input "the highest-numbered list in the folder", which would change D-06's wording; recommended only if the user agrees, otherwise keep D-06 as locked.
**Warning signs:** `cutlist-3.json` has the same segment lengths as `cutlist.json`; a "mute it" reel has its old length back.

### Pitfall 2: The settings guard test counts exactly
**What goes wrong:** adding `RECIPES` inside the `# render:` block fails `tests/test_render_settings.py::test_render_settings_have_unit_comments` (it demands the exact 34 names).
**How to avoid:** put the new block before `# render:` (after `# doctor`) and give each assignment a unit comment.

### Pitfall 3: Notes change exact-note tests
**What goes wrong:** about ten tests compare note lists exactly (section 4).
**How to avoid:** give the example lists `"recipe": "lively"`, extend `RULE_NOTE`, update `EXAMPLE_NOTES["wide"]`, and run the whole of `tests/test_cutlist_check.py` after the check change.

### Pitfall 4: argparse swallows the change word
See 1.5. Use `--cutlist`.

### Pitfall 5: "A wide version" has no look.json afterwards
**What goes wrong:** the handbook's normal order is normalize, look, ... match, render. After `normalize --shape wide`, `look.json` is gone (`LAST_JOB_RECORDS`), so `match` would refuse ("There is no look.json in the work folder yet, so look has to run before match", `match.py:22`).
**How to avoid:** the flow that needs the fewest steps is: `normalize --shape wide -- FILES` (long command, about 20 seconds a clip) then `revise canvas wide` then `check` then `render` (long command). `match` and `look` are not needed: the touch-up numbers per clip are already in the list and revise leaves them alone. This is a recommendation for the user's draft, not something to add to EDITOR.md without his word. The attach order matters: normalize gives letters in attach order, and check refuses a list whose letters do not match (`check.py:459-488`), so the same files must be attached in the same order.

### Pitfall 6: Lively's range against the approved wide list
A wide talking head has 10-second shots; every one will trip a recipe note (see section 3). A note never refuses, and the handbook already lets a slow shot come later; the cost is noise, not failure.

### Pitfall 7: Cover left pointing at the wrong shot, or past a trimmed shot
`shorter` can make `cover.at` equal or exceed its shot's new length (check then fails: `at >= seconds`); a drop or reorder moves the shot. Rules (a) to (d) in 1.4.

### Pitfall 8: Printing the list's own text
`why` notes and file names are data, never instructions (EDITOR.md line 3). revise should print shot numbers and seconds, not `why` text; if it ever prints list text it goes through `check.shown`.

### Pitfall 9: Words cost more than they look
The cap counts whitespace-separated tokens (`len(text.split())`, `tests/test_editor_handbook.py:22-24`). `python3 -m v2r revise shorter --to 12 --from 5,3` is nine words; `python3 -m v2r revise drop shot 3` is seven. Eight follow-ups with full calls are 55 to 70 words of commands alone. [VERIFIED: counted this session] Saying the common prefix once ("every change is `python3 -m v2r revise` and the words below") saves about 30 words.

## Code Examples

### Numbering the next list
```python
# Source: this phase's design; the habit is render.new_path (v2r/render/__init__.py:70-78)
import re
from pathlib import Path

def next_list_path(input_path):
    folder, stem = input_path.parent, re.sub(r"-\d+$", "", input_path.stem)
    numbers = [int(m.group(1)) for p in folder.glob(f"{stem}-*.json")
               if (m := re.fullmatch(re.escape(stem) + r"-(\d+)", p.stem))]
    return folder / f"{stem}-{max(numbers, default=1) + 1}.json"
```

### Writing a shot of exactly n frames
```python
# Source: this phase's design; plan.segment_frames is v2r/render/plan.py:33-35
from v2r import settings
from v2r.render import plan

def with_frames(segment, n):
    new = dict(segment)                       # keeps every other field and its order
    new["to"] = round(segment["from"] + n / settings.OUTPUT_FPS, 3)
    if plan.segment_frames(new)[1] != n:      # never expected; the loop test proves it
        new["to"] = round(segment["from"] + n / settings.OUTPUT_FPS, 6)
    return new
```

### The change-word command line (tested this session)
```python
# Source: throwaway argparse experiment; shapes only
common = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
common.add_argument("--work", type=Path, default=None)
common.add_argument("--cutlist", type=Path, default=None)
revise = commands.add_parser("revise", allow_abbrev=False)
change = revise.add_subparsers(dest="change", required=True)
shorter = change.add_parser("shorter", parents=[common], allow_abbrev=False)
shorter.add_argument("--to", type=float, required=True)
shorter.add_argument("--from", dest="shots", required=True)
```

## The follow-up menu (facts for the user's draft; EDITOR.md gets only his words)

| She says | Call (after `python3 -m v2r revise`) | Fields that change | When to offer it (D-04) |
|----------|----------------------------------------|--------------------|--------------------------|
| shorter | `shorter --to SECONDS --from SHOTS` | `segments[i].to` for trimmed shots; `cover` only if its moment is trimmed away; shots dropped (printed) only when every shot is at its floor | always |
| longer | `longer --to SECONDS --from SHOTS` | `segments[i].to` | always, if any shot has room |
| start with that shot | `reorder N,N,...` | the order of `segments`; `cover.segment` follows its shot | always |
| drop a clip / drop that shot | `drop C` / `drop shot N` | the removed `segments`; `cover` follows or is cleared | always |
| mute it | `sound off` (`--shot N` for one) | `segments[i].sound` | only if sound is kept somewhere |
| keep the sound | `sound keep` | `segments[i].sound` | only if sound was muted |
| a wide version / a tall version | after `normalize --shape wide`: `canvas wide` | `canvas.width`, `canvas.height` | only for a tall reel (and the reverse) |
| move the frame | no revise call: Claude edits `focus_x`/`focus_y` in the list itself and renders | the list is edited by hand into a new numbered file | only when check noted a crop that keeps little |

Also: a different moment, a different star or a new shot is the chat's Claude editing the list (CONTEXT domain). Whether those edits are saved as a numbered file by hand is for the user's draft to say.

## The time estimate (D-03) and its evidence

The rule: **about a minute per clip plus three, rounded up.** Evidence from `docs/phone-limits.md` (opened this session):

| Row | What ran | Measured | Rule says | Fit |
|-----|----------|----------|-----------|-----|
| 15 (Stage 16) | four attachments, tall; same reel wide | tall "about 4 min from the request to the file" (normalize about a minute, about 20 s a clip, look about 20 s); wide "about 5 min"; a second render after one shot's focus moved "about 2 min more" | 4 + 3 = 7 min | the rule is 2 to 3 minutes high |
| 17 (Stage 17) | seven attachments, a hand-written message "Make a reel, about 20 seconds." | "About 9 to 11 minutes from the message to the reel, about 3 of them converting the seven files." | 7 + 3 = 10 min | matches |
| 18 (Stage 18) | a reel on the Stage 18 branch | "The stage changed only the handbook's words, so nothing new was measured" | none | no data |
| 12 (for context) | three clips under 20 s | normalize "about 1 min 41 s"; look about 28 s; join about 1 min 42 s | 3 + 3 = 6 min | in range |

[VERIFIED: docs/phone-limits.md rows 12, 15, 17, 18] Reading: the rule is a fair upper bound at four to seven short clips and is least trustworthy for long clips (the 3-minute clip of row 4 alone took about 467 seconds to join) and above about ten files (no data). "Rounded up" has nothing to round when clips are whole numbers; it can only mean "say a whole number of minutes". Follow-up estimates have one data point (row 15: about 2 minutes for a second render; a wide version adds the conversion, about 20 s a clip). Whether to estimate follow-ups is for the user's draft to say. The reel log (Stage 20) will show drift.

## The handbook: word budget and what the new section replaces

Current: **1,309 words** (`wc -w EDITOR.md`, which equals the test's rule), cap `MAX_WORDS = 1500`. Words per paragraph (counted this session): title 5; opening 39; Who wins 35; **Before editing 86**; steps heading 4; step lines 19, 48, 23, 22, 22, 20, 30, 24 (= 208); Long commands 84; Reading the sheets 104; Choosing and ordering 173; Two recipes 38; Framing 138; Movement 35; Colour 27; **Sound 76**; Numbers in the list 57; **Before sending 89**; **When things go wrong 76**; Just joining 35.

Sentences the new section will fold in or replace (counted):
| Where | Sentence | Words |
|-------|----------|-------|
| Before editing | "If the message does not say what the reel is about, or which moment matters most, ask those two things in one short message and wait. Ask nothing else." | 29 |
| When things go wrong | "Anything else that fails: show the user the error's exact words and stop." (D-05 replaces it) | 13 |
| Before sending | "With the reel, write one or two lines on what is in it, naming clips by what is in them, never by letter." (the reply rule moves) | 23 |
| Step 8 | "Show the cut list as text when asked." (stays or moves) | 8 |
| Before editing | the defaults sentence ("Unless told otherwise: about 20 seconds, tall ...") is about 30 words; the brief's defaults repeat it, so it can fold into the brief | ~30 |
| Sound | the music sentence (35 words) stays as is; Stage 18 put it there | 0 |

Folding the first three out frees **65 words** (up to ~95 with the defaults sentence); room under the cap is then **256 words** (1,500 − 1,244). Estimated cost of the section (my estimate, not a draft): brief with four questions and defaults 60 to 80; the two skip rules 25; the one further question 15; the estimate line 25 to 35; the reply 30; the follow-up menu with calls, fields and "when to offer" 120 to 170; errors with next step 25; work folder gone 25 to 30; fresh chat 12; the newest-list rule 15. Total **350 to 450** words, so the whole handbook is about **1,550 to 1,700**. [ASSUMED: estimates; the user's draft will give the real number] The 1,800 fallback of D-17 is likely; it needs a dated line in `docs/decisions.md`, `MAX_WORDS = 1800` in `tests/test_editor_handbook.py:10`, and the test's own text ("at most 1,500 words", the docstring on line 1 and `test_a_text_of_exactly_1500_words_passes_and_1501_fails_the_cap`) updated together. The planner should not edit EDITOR.md; the draft goes to this phase folder (a `07-HANDBOOK-DRAFT.md`, as Stage 17 had `05-HANDBOOK-DRAFT.md`) for the user's approval.

## The phone side

- **Branch name.** The skill clones `main` or, if the message names a branch, that branch: [VERIFIED: skill/vid2reel/SKILL.md step 1] `or of another branch if the user's message names one (for example "use branch stage-15-look" means `--branch stage-15-look`)`. It clones into a temporary folder (`D=$(mktemp -d)`) and says "Run every later command from that folder", so `work/` lives inside that clone. The phone test message is "use branch stage-19-conversation, make a reel".
- **Pasted list.** EDITOR.md step 4: [VERIFIED: EDITOR.md:13] "A list the user pastes is saved exactly as pasted." It is saved as `work/cutlist.json`. After a wipe, a list offered back as text can be saved the same way; the `clips` block then guards the letters (check names a mismatch: "Clip B in this list was X, but B in the work folder is Y"), so the clips must be attached again in the same order.
- **Names of outputs.** The reel is `work/reel-SHAPE-YYYYMMDD-HHMMSS.mp4` (`render/__init__.py:73`), never overwritten (`-2`, `-3` appended on a clash); its cover is `reel-SHAPE-STAMP-cover.jpg` beside it (`render/proof.py:62`, `reel.with_name(f"{reel.stem}-cover.jpg")`); the proof sheets are `work/proof/proof-NN.jpg`, replaced on each render (`proof.py:16`, `LAST_PROOF`); `render`'s last printed line is the reel's path (`__main__.py:134-140`, `print(reel)`). So each follow-up render adds a new reel file and keeps the old one; the handbook's loop is: `revise ...` (instant, foreground) → `check NEWLIST` is already done by revise's closing report → `render NEWLIST` as a long command → look at the proof sheets → send the new reel.
- **Timing.** revise needs no FFmpeg and takes well under a second, so it never needs the background routine; render does (row 15: a render took about 2 to 3 minutes).
- **Mac-only switches.** The handbook never names `--work` (guard at `test_editor_handbook.py:67-70`). The rehearsal prompt adds it on the Mac, including to `revise`. `--cutlist` is not Mac-only (the phone needs it to name the newest list) and no guard forbids it.

## Rehearsals and the phone test

**How Stage 17 rehearsed.** [VERIFIED: .planning/phases/05-stage-17-editor-s-handbook/05-CONTEXT.md:28] "The rehearsal ... runs in a fresh Claude Code session after /clear, never in the orchestrating session, once per fixture set. Five sets exist in fixtures/ ... Each rehearsal ends with the list of places where EDITOR.md was unclear or tempting to leave". The kit is `.planning/phases/05-stage-17-editor-s-handbook/05-REHEARSAL.md`: blanks for set, profile and message; Mac adaptations (`uv run python -m v2r`, `--work work/<SET>`, never `normalize` without `--work`); a Reads rule (only EDITOR.md, the schema, the attached files and the commands' own output); a closing request for three lists (unclear places, Mac adaptations, files read beyond the allowed). Per 05-07-SUMMARY, the sessions were fresh Claude desktop sessions started by the orchestrating session on the user's word.

**For this stage.** Reuse that kit with a new message each time, using fixture sets "set 1" to "set 5" (the planner should not name folders):
1. nothing but the clips (no message text): the brief must be asked in one message with defaults, then the session stops and waits;
2. "make a reel": same, the brief asked;
3. "20 seconds, calm, tall": only the questions not answered are asked (about, star moment);
4. "just make it": no brief, the reel is made;
5. "wide, for long-form video": shape and length answered; wide throughout;
6. one set that includes a file over `MAX_ATTACHMENT_BYTES` (400 MB), attached without the Mac-only `--no-size-limit` switch so normalize leaves it out with its own sentence: the reply must carry that sentence plus one sentence of next step, and the rest of the reel is still made;
7. (added by this research) "work folder gone": after a finished rehearsal delete `work/<SET>/` and say "shorter"; Claude must ask for the clips again;
8. (added) a follow-up chain on one set: "shorter", then "mute it", then "a wide version"; compare `cutlist.json`, `-2`, `-3`, `-4` side by side as text.

**A new difficulty.** A brief is a conversation: the rehearsing session asks and stops, so someone has to answer. In Stage 17 the sessions ran from one message. Here the user (or the orchestrating session on his word) replies in the same fresh window with an answer such as "1 beach day, 2 the big wave, 3 lively, 4 fine". The kit therefore needs a "turn 2" paragraph; it is the planner's job to add it to a `07-REHEARSAL.md`.

**The guide's brief-versus-"just make it" comparison** (field-guide s19, Do-this step 4): make the same fixture reel twice, once with full answers and once with only "just make it", and watch both with her; the briefed reel should be clearly better. This is a human judgement and goes in the phone-test script and the reel log (`fixtures/reel-log.md`, never in the repo).

**The phone test (CONV-07 / D-21).** On branch `stage-19-conversation`, inside a Project with a Reel style section: attach clips, "use branch stage-19-conversation, make a reel", answer the brief; then "shorter", "mute it", "a wide version". What to compare: the numbered lists side by side. Expect: after "shorter", the same shots, less of them (every `from` unchanged, every `why` unchanged, only `to` values smaller); after "mute it", only `sound` values changed; after "a wide version", only canvas width and height changed (and the clips were normalized again). What to look and listen for, at what time: after "shorter", the opening frame of the reel must be the same picture as before (shots are trimmed at their ends); after "mute it", silence from 0:00 to the end (check should have noted "This reel has no sound at all." only if no shot keeps sound); after "a wide version", the sideways shots are shown whole and the upright ones are cropped to fill, 1920 by 1080, and a note about a crop that keeps little may appear. Time one reel from send to saved for the reel log.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Stage 17: two questions asked only when the message leaves them out | Stage 19: a four-question brief straight away, with defaults | this phase | the two questions fold into the brief |
| Stage 17: "show the user the error's exact words and stop" | quote the tool's sentence and add one next step | this phase | CONV-06 |
| Music questions and a song in the reel | no music from the tool (Stage 18, 2026-11-03) | 2026-11-03 | no music question, no track in the reply |
| A follow-up re-runs the handbook | a follow-up edits the existing list with `revise` | this phase | the guide's Watch-out |

**Deprecated/outdated:** CONV-01, -04, -05, -07 wording and success criteria 2, 3 and 5 (music words).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | No suitable open-source library exists for "trim named shots to a target"; nothing is added to `docs/licenses.md` | Standard Stack | Low: a library would add a dependency for dozens of lines of integer maths |
| A2 | `frames(x + n/30) = frames(x) + n` makes writing `to = from + n/30` exact for any `from` | 1.2, 2 | Low: the loop test over off-grid `from` values proves or disproves it before shipping |
| A3 | A drop can overshoot, so the result may land under the target by up to one shot's floor; the plan accepts and reports that | 2 | Medium: the user may prefer a refusal; Open Question 4 |
| A4 | The handbook section will cost 350 to 450 words and the whole will need the 1,800 cap | The handbook | Medium: the cap decision can wait for the draft |
| A5 | Giving leftover single frames to the last unnamed shots protects the opener | 2 | Low: any fixed rule satisfies the tests; the planner may choose another |
| A6 | After a wide re-normalize, `look` and `match` can be skipped because touch-up numbers stay in the list | Pitfall 5 | Medium: confirm in the phone test that the wide reel looks as even as the tall one |

## Open Questions

1. **How do follow-ups find the newest list? (Pitfall 1)**
   - What we know: D-06 says revise reads `work/cutlist.json` unless named; check, match and render also default to it; revise's output is numbered beside the input.
   - What's unclear: whether the default should instead be "the highest-numbered list in the folder".
   - **HANDED TO PLANNER. Recommendation:** keep D-06 as locked; revise's last lines name the exact next commands with the new path; the handbook draft says every command after a revise names the newest list; rehearsal 8 and the phone test compare the numbered lists. Offer the "newest list" default to the user as an alternative in the plan's summary, not as a change.

2. **One recipe note per shot, or one grouped sentence per direction? (D-16)**
   - What we know: D-16 says "one sentence naming the shot and the range"; the approved wide example has three shots over 3 seconds.
   - **HANDED TO PLANNER. Recommendation:** one grouped sentence per direction that still names every shot; wording is code, not the user's.

3. **`shorter` when every shot is at its floor and the named list is exhausted.**
   - D-07 says whole named shots are dropped "until the target is met"; it does not say what happens if the named list (without the first shot) runs out first.
   - **HANDED TO PLANNER. Recommendation:** refuse and write nothing: "Even with shots 6 and 5 dropped the reel is still 9.5 seconds, so name more shots to take it to 9." (Unlike `longer`, which D-08 says writes what it reached.)

4. **A drop that overshoots the target.**
   - **RESOLVED (plan to do this):** decide drops first on floors, trim the survivors exactly, and when the survivors, untrimmed, add up to less than the target, write them and say how far under the reel is.

5. **Cover cases D-09 leaves open.**
   - **RESOLVED (recommendation adopted unless the user objects):** rules (a) to (d) in 1.4: renumber when the shot moves or an earlier shot goes; clear when the shot is dropped or its moment is trimmed away; say so in a printed line.

6. **Should `longer` stop at the next shot of the same clip?**
   - **HANDED TO PLANNER. Recommendation:** yes, stop an extension at the first frame of any later shot of the same clip that begins after this shot begins (check allows overlaps, so nothing else prevents the reel showing the same footage twice).

7. **A drop that leaves the reel under 3 seconds.**
   - **HANDED TO PLANNER. Recommendation:** write the list, let the closing check print the problem, exit 1; refuse only when no shot is left (the schema's `minItems`).

8. **Command grammar.**
   - **RESOLVED:** `revise CHANGE ... [--cutlist PATH] [--work FOLDER]`, with the changes `shorter`, `longer`, `reorder`, `drop`, `sound`, `canvas` (tested, section 1.5).

9. **Does revise run the checker at the end?**
   - **RESOLVED:** yes, per section 1.6, with exit 1 if the new list has a problem.

10. **The word cap.**
    - **HANDED TO PLANNER and the user.** Plan the draft first, count it, and raise `MAX_WORDS` to 1,800 only if the tightened whole is over 1,500, with the dated decisions line (D-17).

11. **The wide-version order of commands (normalize wide, revise canvas, check, render; no look or match).**
    - **HANDED TO the user's draft.** Reasoned from code (Pitfall 5); confirm on the phone.

12. **Does the estimate cover follow-ups?**
    - **HANDED TO the user's draft.** One data point exists (about 2 minutes for a second render).

13. **"Rounded up" in the estimate rule.**
    - **RESOLVED:** harmless; with whole clips the rule is already whole minutes.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.13 via uv | revise, tests | yes | `uv run pytest` ran this session | none needed |
| `jsonschema` | check's schema pass | yes | 4.26.0 pinned | none needed |
| pytest | tests | yes | ran 287 tests in 6.9 s | none needed |
| FFmpeg | rehearsals and the phone test only (not revise, not its tests) | not probed (not needed for the code or its tests) | the sandbox has 6.1.1 per `docs/phone-limits.md` | none needed |

**Missing dependencies with no fallback:** none.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.x |
| Config file | `pyproject.toml` (`testpaths = ["tests"]`, as in 05-VALIDATION.md) |
| Quick run command | `uv run pytest tests/test_revise.py tests/test_cutlist_check.py tests/test_editor_handbook.py tests/test_render_settings.py -q` (about 10 seconds) |
| Full suite command | `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" run-with-timeout 1800 -- uv run pytest -q` (macOS has no `timeout`; Stage 17 recorded 11 to 19 minutes) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CONV-01 | brief of four numbered questions with defaults, answered ones left out, "just make it" skips | guard test on EDITOR.md (section heading "Talking with her" present, within the cap, no Mac-only switch) plus rehearsals 1 to 4 plus the briefed-versus-plain comparison | `uv run pytest tests/test_editor_handbook.py -q`; rehearsal and human | guard: extend `tests/test_editor_handbook.py` (Wave 0); rehearsal kit: Wave 0 |
| CONV-02 | at most one question after looking | rehearsal (a case where the named moment is not on the sheets) | human, fresh session | kit: Wave 0 |
| CONV-03 | one line with an estimate, then silence | rehearsal checks the first reply and the silence; phone test with a stopwatch | human | kit: Wave 0 |
| CONV-04 | two lines, three follow-ups from the menu, no letters, no track | rehearsal; a handbook guard that `revise` is named and that every revise call written in EDITOR.md parses (feed each `python3 -m v2r revise ...` line in the text to the real parser with placeholder numbers) | `uv run pytest tests/test_editor_handbook.py -q`; rehearsal | extend (Wave 0) |
| CONV-05 | each change alters only its own fields; target met to the frame; numbering; refusals | pytest, whole-list before and after for each change, both shapes, plus loop tests | `uv run pytest tests/test_revise.py -q` | Wave 0 (new file) |
| CONV-05 (recipe) | `recipe` in the schema; assumed note; range notes; floors and ceilings in settings; EDITOR.md's recipe sentence in step with them | pytest | `uv run pytest tests/test_cutlist_check.py tests/test_render_settings.py tests/test_editor_handbook.py -q` | extend existing files (Wave 0) |
| CONV-06 | plain errors with a next step; work folder gone means ask for clips again | pytest: every refusal is one `v2r revise: ...` sentence, no traceback, exit 1, no file written, including a missing work folder and a missing list; rehearsals 6 and 7 for the next-step sentence | `uv run pytest tests/test_revise.py -q`; rehearsal | Wave 0 |
| CONV-07 | phone test: attach, brief, reel, "shorter", "mute it", "a wide version" | human, on the branch, per D-21 | phone | none (human) |

### Sampling Rate
- **Per task commit:** the quick run command above.
- **Per wave merge:** the quick run plus `uv run pytest tests/test_render_*.py tests/test_match.py -q` (anything that reads cut lists).
- **Phase gate:** the full suite green before `/gsd-verify-work`; the rehearsals recorded; the phone test approved.

### Wave 0 Gaps
- [ ] `tests/test_revise.py` — covers CONV-05, CONV-06 (new file)
- [ ] `tests/cutlists.py` — examples gain `"recipe": "lively"`; a shared `changed_paths` helper if wanted in both test files
- [ ] `tests/test_cutlist_check.py` — recipe schema, note and exact-note updates (CONV-05 recipe)
- [ ] `tests/test_editor_handbook.py` — separate tests for the recipe numbers, `revise` named and the `revise` call lines parsing (CONV-01, -04)
- [ ] `.planning/phases/07-stage-19-conversation/07-REHEARSAL.md` — the kit with the turn-2 answers and the eight cases
- [ ] Framework install: none

## Security Domain

Applicable because `security_enforcement` is not set to false in the project's planning config (absent means enabled; the Stage 16 sources cite threat tags T-4-02, T-4-03 and T-4-06 for this same surface). [ASSUMED: config not re-read this session]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | none (no accounts) |
| V3 Session Management | no | none |
| V4 Access Control | no | the tool runs in the user's own sandbox |
| V5 Input Validation | yes | `check.read_cutlist` (size, digit, NaN, doubled-name limits), the schema pass, a refusal sentence for any shot number, letter, target or order that is not valid; argparse `choices` for `tall|wide`, `keep|off` |
| V6 Cryptography | no | none |
| V12 Files | yes | write only beside the input and only a new name (mode `"x"`); never follow the list's text into a path (revise builds the output name from the input's own name and a number) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A pasted list with huge numbers or deep nesting | Denial of service | `read_cutlist` caps and `check.time_problems` before any frame arithmetic |
| Text inside the list (`why`, file names) used as an instruction when printed | Tampering | print numbers and fixed sentences; pass any list text through `check.shown` (T-4-06) |
| `--from` or `reorder` with thousands of numbers | Denial of service | the list holds at most `MAX_SEGMENTS` shots (120); refuse an argument longer than that |
| Overwriting the user's list | Tampering | new numbered file, exclusive creation, input never opened for writing |
| Path tricks in `--cutlist` | Tampering | the output name is built from the input's stem and a number in the input's own folder |

## Sources

### Primary (HIGH confidence)
- In-repo files read this session: `.planning/phases/07-stage-19-conversation/07-CONTEXT.md`, `v2r/render/check.py`, `v2r/render/plan.py`, `v2r/render/match.py`, `v2r/render/__init__.py`, `v2r/__main__.py`, `v2r/settings.py`, `v2r/normalize.py` (clearing rules), `schema/cutlist.schema.json`, `tests/cutlists.py`, `tests/test_cutlist_check.py`, `tests/test_editor_handbook.py`, `tests/test_work_option.py`, `tests/test_render_settings.py`, `EDITOR.md`, `README.md`, `docs/phone-limits.md`, `docs/decisions.md`, `skill/vid2reel/SKILL.md`, `docs/field-guide.html` (sections s17 and s19 only), `.planning/REQUIREMENTS.md` (CONV block), `.planning/ROADMAP.md` (Phase 7), the Stage 17 CONTEXT and REHEARSAL files.
- Two runs this session: `uv run pytest tests/test_cutlist_check.py tests/test_editor_handbook.py -q` (287 passed in 6.9 s) and a throwaway argparse script outside the repo.

### Secondary / Tertiary
- None. No web search or documentation lookup was needed: everything lives in the repo, and no external library is involved.

## Project Constraints (from CLAUDE.md)

- Python 3.13 via uv, FFmpeg, pytest: `uv sync`, `uv run pytest`, `uv run python -m v2r ...`; the sandbox has no uv and installs `requirements.txt` with pip (regenerate it after any `uv add`; this phase adds no package).
- Three jobs never mix: look measures; the cut list holds every edit decision and is written by the chat's Claude; render builds exactly what the list says; normalize first. revise is a mechanical transform, decides nothing.
- Originals are never modified; every output is a new file. Every number that controls behaviour lives in `v2r/settings.py`.
- EDITOR.md is the user's: keep it short and plain, never move its content into code or the skill; at most 1,500 words guarded by a test (raise to 1,800 only with a decisions line); taste never goes in EDITOR.md or the repo.
- House rules: no filters by default; every shot fills the tall frame; tall and wide are one setting, no command, default or test may assume tall (every revise test runs in both shapes).
- The sandbox is the truth: Python and FFmpeg only; 30 MiB back; any command stopped after 2 minutes. After any change to how video is processed, tell the user to test from a phone before merging. You cannot watch video or hear audio: say exactly what to look or listen for, and at what time.
- Public repo: never commit video, photos or audio from `fixtures/` or `work/`, any name or account, or any secret; no Co-Authored-By or other attribution lines in commits (CLAUDE.md; commit messages for this phase carry none). Before writing something from scratch, check for an open-source library and list it in `docs/licenses.md`.
- When a Decide box is settled or the build differs from the guide: write the decision into CLAUDE.md and add a dated line to `docs/decisions.md` (never naming a person or account). Where those disagree with the guide they win.
- GSD phases and branches are named by guide stage (`stage-19-conversation`); nothing merges into main until the user has made a reel from a phone on the branch.
- GSD workflow: file changes go through a GSD command.
- Explain every change in plain English; the user is not a programmer.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependency; everything reused was read.
- Architecture and mechanics: HIGH — each function, line range and quote above was read this session; the argparse behaviour was run.
- Trimming arithmetic: MEDIUM — derived by reasoning from `plan.frames` and `plan.segment_frames`; the loop tests in section 4 turn it into a proof.
- Handbook budget and estimate rule: MEDIUM — estimates and three data points.
- Pitfalls: HIGH — each came from a file or test read this session.

**Research date:** 2026-11-03
**Valid until:** 2026-12-03 (stable; invalidated if `check.py`, `plan.py` or the cut list schema change before planning)
