---
phase: 07-stage-19-conversation
fixed_at: 2026-11-04T23:26:07Z
review_path: .planning/phases/07-stage-19-conversation/07-REVIEW.md
iteration: 1
findings_in_scope: 11
fixed: 4
skipped: 7
status: partial
---

# Phase 7: Code Review Fix Report

**Fixed at:** 2026-11-04T23:26:07Z
**Source review:** .planning/phases/07-stage-19-conversation/07-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 11 (0 Critical, 3 Warning, 8 Info)
- Fixed: 4 (WR-01, WR-02, WR-03, IN-03), one commit each
- Left as is by design: 1 (IN-07)
- Not chosen for this pass: 6 (IN-01, IN-02, IN-04, IN-05, IN-06, IN-08)

The user chose which findings to fix; the rest are listed under Skipped with the reason. EDITOR.md was not touched: the handbook wording the reviewer proposed, plus one new sentence, is under "For the user to paste into EDITOR.md" at the end.

## Fixed Issues

### WR-01: A write that fails at close leaves a truncated `cutlist-N.json` behind

**Files modified:** `v2r/render/revise.py`, `tests/test_revise.py`
**Commit:** ba46aa3 — `fix(07): WR-01 remove the half-written list when a revise write fails at close`
**Applied fix:** `write_new` now puts the create, the write and the close of the new list inside one `try`. A `FileExistsError` still means "try the next number". Any other `OSError` or `ValueError` (a full disk shows up when the file is closed, because a small list sits in Python's buffer until then) now removes the half-written file before raising `ReviseError(NO_WRITE)`, so "nothing was changed" is true and the number is not used up. A failed removal is swallowed rather than becoming a Python traceback. The reviewer's `os.link` idea (temp file, then hard link) was not taken: the one `try` is enough to leave no file behind, and a hard link is one more thing that can differ between the Mac and the sandbox.
**Tests added:** `test_a_write_that_fails_at_close_leaves_no_half_written_list` (tall and wide). It swaps revise's `open` for one whose file takes the first hundred characters and raises `OSError(28, "No space left on device")` when closed, then checks the exit code is 1, the message is the existing `NO_WRITE` sentence, `cutlist-2.json` does not exist and the folder is as it was. Run against the old code it fails (a 100-byte `cutlist-2.json` is left); with the fix it passes.

### WR-02: Without `--cutlist`, revise silently starts from the first list

**Files modified:** `v2r/render/revise.py`, `tests/test_revise.py`
**Commit:** bdab4a6 — `fix(07): WR-02 say when a revise started from the first list while a newer one exists`
**Applied fix:** No change of behaviour: the D-06 default (start from `work/cutlist.json`) stands and revise still chooses no list. The folder scan that `next_list_path` already did was moved into one helper, `list_family(path)`, which returns the family's stem and the highest `cutlist-N.json` number beside the list, using the same pattern and `settings.REVISE_NUMBER_DIGITS` as before (no new literal). `next_list_path` uses it as before; a new `newest_list_path(path)` returns the highest-numbered list or `None` when there is none. In `run`, only when `--cutlist` was not given and a numbered list exists, one note is printed right after the "New cut list:" line, in revise's own voice:

`Note: this change started from work/cutlist.json, but a newer list exists, work/cutlist-3.json. To change the newest list, add --cutlist work/cutlist-3.json after the change word.`

The same note is printed on the "nothing was changed" path, after the "is still the list to use." sentence. Nothing is printed when `--cutlist` was given, even when it names `cutlist.json` itself. The newest list is looked up before the new one is written, so the note never names the list revise has just made. The sentence lives in one constant, `NEWER_LIST`.
**Tests added:** four tests, each tall and wide: the note appears as the second line and names `cutlist-3.json` (not `-2`) when `cutlist-2.json` and `cutlist-3.json` exist and the flag is absent, and appears exactly once; no note without a numbered list, none when `--cutlist` names the newest list, none when `--cutlist` names the first list on purpose; the list written with the note is byte-for-byte the list written without it, and the placeholder `cutlist-3.json` is untouched; the note is printed on the "nothing was changed" path too, and no file is written there. Because `check` prints "Note:" lines of its own, the tests look for the words "but a newer list exists".

### WR-03: The clip-letter pattern written twice

**Files modified:** `v2r/render/revise.py`, `tests/test_revise.py`
**Commit:** fe9ece3 — `fix(07): WR-03 read clip letters in drop with look's one letter pattern`
**Applied fix:** `v2r/render/check.py` already imports `look` from `v2r` and reads letters with `look.LETTER.fullmatch`, so render already depends on look and no new dependency direction was needed. `revise.py` now imports `look` the same way and `change_drop` uses `look.LETTER.fullmatch(words[0])` instead of its own `re.fullmatch("[A-Z]{1,3}", ...)`. The comment that this is normalize's and the schema's pattern, not a new limit, is kept and now says where the one definition lives. One trap was fixed on the way: `change_drop` had a local variable named `look` (the list's own "look" field) that would have shadowed the module and crashed the whole-clip branch; it is renamed `look_block`. The pattern stays in `v2r/look/__init__.py` (line 63) because that is where check already reads it from; moving it to normalize would have meant touching look and check for no gain.
**Tests added:** `test_drop_reads_clip_letters_with_looks_one_pattern`: with `look.LETTER` swapped for a lower-case pattern, `drop a` is read as a letter ("There is no clip a in this list's shots...") and `drop A` is no longer one (`DROP_WORDS`), proving drop reads letters through the shared pattern. The existing drop tests pass unchanged.

### IN-03: "shots 3 dropped" for one shot

**Files modified:** `v2r/render/revise.py`, `tests/test_revise.py`
**Commit:** 5ad7f71 — `fix(07): IN-03 say shot, not shots, when one dropped shot is named`
**Applied fix:** The refusal in `change_shorter` now reads "shot 3 dropped" for one shot and keeps "shots 7 and 6 dropped" (the existing `check.letters_sentence` style) for several.
**Tests added:** `test_one_dropped_shot_is_called_shot_not_shots` (tall: `shorter --to 6 --from 3`, "would be 9 seconds"; wide: `shorter --to 5 --from 3`, "would be 6 seconds"), checking the whole sentence and that nothing was written. The existing two-shot test (`shots 7 and 6 dropped`) passes unchanged.

## Skipped Issues

### IN-07: Terminology differs between check and revise

**File:** `v2r/render/check.py:716-720`
**Reason:** Not changed, by design. check speaks in the list's own field name, "Segment N", in every message it has printed since Stage 16; changing only the new recipe note would make check inconsistent with itself, and changing all of check is outside this fix. The handbook's "shot" and check's "Segment" number the same thing: shot 3 in revise's lines is Segment 3 in check's.
**Original issue:** The new recipe note says "Segments 2 and 3 last less than ...". Everything revise prints, and the handbook, says "shot". The user sees both on one screen.

### IN-01: `shorter` also trims shots the chat did not name, and breaks ties by position

**File:** `v2r/render/revise.py:377-389`
**Reason:** Not chosen for this pass. The reviewer proposed no code change (it matches D-07 and every trimmed shot is printed); the wording side is in "For the user" below.
**Original issue:** After the named shots reach their floors, the remainder is spread over every unnamed shot, with leftover frames taken one each from the later shots.

### IN-02: `set_frames` can fail for a start with many decimals at an exact half frame

**File:** `v2r/render/revise.py:326-332`
**Reason:** Not chosen for this pass. Times in a list have one or two decimals, so the failing case (a start with eight decimals) does not arise from the handbook's lists; the refusal is one plain sentence and nothing is written.
**Original issue:** A start such as 5.28333303 with an end exactly half a frame away fails all three tries and is refused.

### IN-04: Argument-parser errors are usage text, not one sentence

**File:** `v2r/__main__.py:105-106`
**Reason:** Not chosen for this pass. Affects `reorder 2 1 3` unquoted, `--work` or `--cutlist` before the change word, and a missing change word. The fifth handbook sentence below tells the chat where `--cutlist` goes, which covers the likeliest case without a code change.
**Original issue:** These inputs end in argparse's multi-line usage text with exit code 2, and the handbook says to quote the tool's sentence.

### IN-05: Printed "Next:" commands cut long paths and do not quote spaces

**File:** `v2r/render/revise.py:62-65, 573-579`
**Reason:** Not chosen for this pass. Neither happens with `work/` in the sandbox, which is what her phone runs; both can only happen on a Mac with `--work`.
**Original issue:** `shown_path` cuts a path over 200 characters and prints a path with a space unquoted.

### IN-06: `why` and label text go stale after `shorter` and `longer`

**File:** `v2r/render/revise.py:446, 543`
**Reason:** Not chosen for this pass. The reviewer's own advice is to leave it: revise must not rewrite the chat's words, and the proof sheets show the real frames.
**Original issue:** Only "to" changes, so a shot's "why" can name an end the shot no longer has.

### IN-08: Case-insensitive filesystems can exhaust the name tries

**File:** `v2r/render/revise.py:67-85, 91-102`
**Reason:** Not chosen for this pass. Mac-only (a list passed as `Cutlist.json`); the sandbox's filesystem is case-sensitive and the handbook's paths are all lower case. Note for a later pass: the folder scan now lives in one place, `list_family`, so both the `re.IGNORECASE` and the `digits_pattern()` on the stem would be a one-line change each.
**Original issue:** `next_list_path` matches names case-sensitively, so every try picks the same taken name and the user gets `NO_WRITE`.

## Verification

- Each fix: Python syntax check (`ast.parse`) of both files, then `tests/test_revise.py` (and `tests/test_cutlist_check.py` for WR-03), green before the commit.
- WR-01's new test was run against the old `write_new` first and failed as expected (a 100-byte `cutlist-2.json` was left behind), then passed with the fix.
- After all four: `uv run pytest tests/test_revise.py tests/test_revise_chain.py tests/test_cutlist_check.py tests/test_editor_handbook.py -q` — **536 passed** in 44 s (523 before the fixes, plus 13 new tests: 2 for WR-01, 8 for WR-02, 1 for WR-03, 2 for IN-03). The full suite was not run here; the orchestrator runs it.
- Where it ran: in an isolated git worktree of the repo (branch `gsd-reviewfix/07-...`, fast-forwarded into `stage-19-conversation` afterwards) with a fresh `uv run` environment from the same `uv.lock`. The numbers are reproducible from the main checkout: the same four commits are now on `stage-19-conversation`.
- Public-repo scan of the four commits: no attribution lines, no absolute paths, no names or e-mail addresses.

**What to look for on the phone (no change to how video looks or sounds):** none of the four fixes touches rendering. The one visible change is the new note: after a first follow-up, a second `revise` typed without `--cutlist` now prints a "Note: this change started from ..." line right under "New cut list:". If the chat follows the fifth handbook sentence below, that note should never appear.

## For the user to paste into EDITOR.md

The reviewer's four suggestions (from 07-REVIEW.md, "For the user"), copied here unchanged, and a fifth that you have not yet approved. EDITOR.md was not edited.

1. **`--cutlist` is never named (see WR-02).** The code builds each revise on `work/cutlist.json` unless `--cutlist PATH` is given. EDITOR.md says "change the newest cut list" and "give it to every later command, like `render work/cutlist-3.json`". `revise` is not in the example, and it needs the flag where the others take the path directly. Suggested wording: "To change the newest list, add `--cutlist work/cutlist-N.json` after the change, N being the number revise last printed."
2. **The `shorter` bullet leaves out two behaviours.** The code (a) trims the shots not named, sharing what is left over after the named ones reach their shortest, and (b) never drops shot 1, so "whole shots go from the end of the list" means the end of the named list. Suggested wording: "The named shots are trimmed first, in order; if that is not enough, the others are trimmed evenly; whole shots go only if even that is not enough, last-named first, and never shot 1."
3. **The `canvas` bullet.** `canvas wide` always ends with a "Problem: ... normalize them again with --shape wide" sentence and exit code 1 until the clips are re-normalized. That is expected and matches your order of steps, but a chat reading "Problem" may stop. Suggested wording: "revise will say the clips need normalizing again; that is the next step, not an error."
4. **The `longer` bullet.** It says it "changes only the 'to' of the shots named". The code can leave a named shot unchanged (already at the recipe's longest, at the end of its clip, or at the next shot of the same clip). It can also stop short of the length asked, and says "needs a new moment added to the list". Suggested wording: "Say what it could not do, and offer to look for another moment."
5. **Not yet approved — the sentence that pairs with WR-02's note:** `On the next revise, add --cutlist work/cutlist-3.json after the change word, using the name revise last printed.`

---

_Fixed: 2026-11-04T23:26:07Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
