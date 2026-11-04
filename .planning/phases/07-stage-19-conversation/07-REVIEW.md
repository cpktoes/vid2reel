---
phase: 07-stage-19-conversation
reviewed: 2026-11-04T00:00:00Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - v2r/render/revise.py
  - v2r/render/check.py
  - v2r/render/__init__.py
  - v2r/__main__.py
  - v2r/settings.py
  - schema/cutlist.schema.json
  - tests/test_revise.py
  - tests/test_revise_chain.py
  - tests/test_cutlist_check.py
  - tests/cutlists.py
  - tests/test_editor_handbook.py
  - EDITOR.md
  - README.md
findings:
  critical: 0
  warning: 3
  info: 8
  total: 11
status: issues_found
---

# Phase 7: Code Review Report

**Reviewed:** 2026-11-04
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

I read all of `v2r/render/revise.py` and the Stage 19 changes in `check.py`, `__main__.py`, `settings.py` and the schema. I ran the four Stage 19 test files (523 passed). I also fuzzed `shorter_frames` and `set_frames` and drove the CLI through the edge inputs named in the brief.

The field-isolation guarantee holds. `run()` works on a deep copy. `reorder` reuses the same shot records. `drop` leaves the clips block and the touch-up alone. The cover follows its shot, or is removed when its shot goes or its moment is trimmed away. The `recipe` field is never touched. Unknown fields survive.

I fuzzed 100,000 random `shorter_frames` cases and found no violation of these rules:
- no shot goes under its floor;
- shot 1 is never dropped;
- the total never goes over the target;
- the total hits the target exactly unless a whole shot had to go.

I fuzzed 200,000 `set_frames` cases. One failed, a start with 8 decimals (IN-02).

The edge inputs are refused in single sentences: `drop shot 0`, `reorder 1,1,2`, `--to 0`, `--to -5`, `--to 1e1`, `--from 1,1`, a shot number past the end and `sound --shot 1.0`.

I found no Critical issues. Three Warnings concern a truncated file left behind by a failed write, a default base list that silently forks from the original, and a hard-coded letter limit. The rest are Info items, plus handbook wording suggestions under "For the user".

## Warnings

### WR-01: A write that fails at close leaves a truncated `cutlist-N.json` behind while saying "nothing was changed"

**File:** `v2r/render/revise.py:94-104`
**Issue:** Only `handle.write()` is inside the inner `try` that unlinks the file. A cut list is a few KB, so Python's text buffer holds it all and the real write happens when the `with` block exits. A full disk, quota or I/O error then raises `OSError` from `__exit__`. That goes to the outer `except (OSError, ValueError)`, which raises `NO_WRITE` without unlinking.

I reproduced it with a small file-size limit. `write_new` raised "The new cut list could not be written beside the old one, so nothing was changed." The folder then held a 100-byte `cutlist-2.json`.

Consequences:
- The message is false, because a junk file now exists.
- Later revises skip that number and write `cutlist-3.json`.
- A reader who globs `cutlist-*.json` or takes the highest number could pick up a truncated list.

**Fix:** Cover the whole create, write and close in one cleanup path. For example:
```python
try:
    with open(target, "x", encoding="utf-8") as handle:
        handle.write(text)
except FileExistsError:
    continue
except (OSError, ValueError):
    target.unlink(missing_ok=True)
    raise ReviseError(NO_WRITE) from None
return target
```
The `x` open has either created the file (so removing it is correct) or raised `FileExistsError`, which is caught first. To make the file appear whole or not at all, write `cutlist-N.json.tmp` and `os.link` it to the final name (`link` fails if the name exists), then unlink the temp.

### WR-02: Without `--cutlist`, revise silently starts from the original `work/cutlist.json`, not the newest list, and the handbook never names `--cutlist`

**File:** `v2r/render/revise.py:564-566`; `v2r/__main__.py:80-83`; `EDITOR.md:43-51`
**Issue:** A second follow-up run as `python3 -m v2r revise sound off` (no `--cutlist`) reads `work/cutlist.json`. That is the list from before the first follow-up. It writes `cutlist-3.json` containing only the new change, so the first change ("shorter") is lost. Nothing warns of this: the run succeeds, check passes, and the numbering looks like a chain. The code does print "Any further change starts from this list: ... --cutlist NEW" after each run. EDITOR.md says "change the newest cut list" but its revise bullets never show `--cutlist`. See "For the user".
**Fix:** Keep the D-06 default, but say when it forks. If `--cutlist` was not given and a higher `cutlist-N.json` exists beside the input, add a first line to the output, for example "Note: cutlist-3.json is newer; this change started from cutlist.json." Revise chooses nothing; it only reports. Refusing, or using the highest-numbered list, would also work, but that changes D-06.

### WR-03: The clip-letter limit is a literal in revise.py, not the shared pattern

**File:** `v2r/render/revise.py:251-252`
**Issue:** `re.fullmatch("[A-Z]{1,3}", words[0], ...)` copies the letter rule ("one to three capitals") that already lives in `look.LETTER` (`v2r/look/__init__.py:63`). `check.clips_problem` uses `look.LETTER` instead of copying the pattern. The comment says it is "not a new limit", but if normalize's letters ever change, `drop` would read letters differently from `check`. Project rule: a literal that controls behaviour belongs in one place.
**Fix:** `from v2r import look` and use `look.LETTER.fullmatch(words[0])`. The `re.ASCII` flag is not needed, because `[A-Z]` is already ASCII.

## Info

### IN-01: `shorter` also trims shots the chat did not name, and breaks ties by position

**File:** `v2r/render/revise.py:377-389`
**Issue:** After the named shots reach their floors, the remainder is spread over every unnamed shot. Leftover frames go "one each from the later shots", a positional tie-break. This matches D-07 and every changed shot is printed, so it is not a bug. It is the one place revise touches shots nobody named, and it is why the handbook line "changes only the 'to' of shots" needs care. My CLI run `shorter --to 15 --from 4,2` on the 7-shot example trimmed all 7 shots.
**Fix:** None needed. Keep each trimmed shot in the printed lines (it is). See "For the user".

### IN-02: `set_frames` can fail for a start with many decimals at an exact half frame

**File:** `v2r/render/revise.py:326-332`
**Issue:** The three tries cover starts with up to about 6 decimals. In my fuzz, `from` = 5.28333303 with a target of 254 frames failed all three tries, because the intended end is exactly half a frame and the start itself is not on a 6-decimal grid. The result is "A shot's end could not be written to the exact frame, so nothing was changed." The chance is tiny, since times in a list have one or two decimals, but the user cannot recover by asking again.
**Fix:** Add a final try that rounds the end up to the start's own precision, or let the last try add one more place (for example 9 decimals), still checked by the same two assertions.

### IN-03: Plural slip: "shots 3 dropped"

**File:** `v2r/render/revise.py:422-426`
**Issue:** With one dropped shot the sentence reads "Even with every shot at its shortest and shots 3 dropped" (I reproduced it with `shorter --to 6 --from 3`). The handbook quotes this sentence.
**Fix:** `"shot" if len(gone) == 1 else "shots"`.

### IN-04: Argument-parser errors are usage text, not one sentence

**File:** `v2r/__main__.py:105-106` and the whole revise parser
**Issue:** These inputs end in argparse's multi-line usage text with exit code 2:
- `reorder 2 1 3` (unquoted, a likely way to type it);
- `--work` or `--cutlist` placed before the change word;
- a missing change word.

The handbook says to quote the tool's sentence, and there is none to quote.
**Fix:** Let `reorder` take `nargs="+"` and join the words with commas before `parse_shot_list`, so `3,1,2` and `3 1 2` both work. For the rest, subclass the parser's `error` to print one sentence, or leave as is and say in the handbook to write `--cutlist` after the change word.

### IN-05: Printed "Next:" commands cut long paths and do not quote spaces

**File:** `v2r/render/revise.py:62-65, 573-579`
**Issue:** `shown_path` uses `clean_text` with the default limit of `FILE_TEXT_CHARS` (200). A path longer than that is cut, so the printed render command names a file that does not exist. A path with a space is printed unquoted. Neither happens with `work/` in the sandbox. Both can happen on a Mac with `--work`.
**Fix:** Use `shlex.quote(clean_text(str(path), limit=len(str(path))))`, or refuse to print a command when the cleaned text differs from the real path.

### IN-06: `why` and label text go stale after `shorter` and `longer`

**File:** `v2r/render/revise.py:446, 543`
**Issue:** Only `to` changes. A shot's `why` such as "A 06.0 to A 08.5: the wave breaks" then names an end the shot no longer has. EDITOR.md's pre-send check looks for "a frame that does not match its why". The proof sheets show the real frames, so this is a wording mismatch, not a rendering bug.
**Fix:** Leave it; revise must not rewrite the chat's words. Optionally add a line to the output such as "Shot 4's why note still names its old end."

### IN-07: Terminology differs between check and revise

**File:** `v2r/render/check.py:716-720` and `v2r/render/revise.py`
**Issue:** The new recipe note says "Segments 2 and 3 last less than ...". Everything revise prints, and the handbook, says "shot". The user sees both on one screen. The older check sentences also say "Segment", so this follows existing practice.
**Fix:** Optional: say "Shot" in the new note. The note-text tests would need updating.

### IN-08: Case-insensitive filesystems can exhaust the name tries

**File:** `v2r/render/revise.py:67-85, 91-102`
**Issue:** `next_list_path` matches names case-sensitively. If a list is passed as `Cutlist.json` and `cutlist-2.json` exists, the folder scan misses it. Each of the `REVISE_NAME_TRIES` (100) attempts picks the same name and gets `FileExistsError`, and the user gets NO_WRITE. This affects Mac use only. Related: `re.sub("-[0-9]+$", ...)` on line 74 uses unbounded digits while the family pattern uses the bounded `digits_pattern()`.
**Fix:** Compare names with `re.IGNORECASE`, and use `digits_pattern()` on line 74.

## For the user

These are wording suggestions for EDITOR.md. No code change is proposed.

1. **`--cutlist` is never named (see WR-02).** The code builds each revise on `work/cutlist.json` unless `--cutlist PATH` is given. EDITOR.md says "change the newest cut list" and "give it to every later command, like `render work/cutlist-3.json`". `revise` is not in the example, and it needs the flag where the others take the path directly. Suggested wording: "To change the newest list, add `--cutlist work/cutlist-N.json` after the change, N being the number revise last printed."
2. **The `shorter` bullet leaves out two behaviours.** The code (a) trims the shots not named, sharing what is left over after the named ones reach their shortest, and (b) never drops shot 1, so "whole shots go from the end of the list" means the end of the named list. Suggested wording: "The named shots are trimmed first, in order; if that is not enough, the others are trimmed evenly; whole shots go only if even that is not enough, last-named first, and never shot 1."
3. **The `canvas` bullet.** `canvas wide` always ends with a "Problem: ... normalize them again with --shape wide" sentence and exit code 1 until the clips are re-normalized. That is expected and matches your order of steps, but a chat reading "Problem" may stop. Suggested wording: "revise will say the clips need normalizing again; that is the next step, not an error."
4. **The `longer` bullet.** It says it "changes only the 'to' of the shots named". The code can leave a named shot unchanged (already at the recipe's longest, at the end of its clip, or at the next shot of the same clip). It can also stop short of the length asked, and says "needs a new moment added to the list". Suggested wording: "Say what it could not do, and offer to look for another moment."

---

_Reviewed: 2026-11-04_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
