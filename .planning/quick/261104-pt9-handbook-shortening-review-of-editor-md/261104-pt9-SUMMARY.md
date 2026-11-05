---
phase: quick-261104-pt9
plan: 01
subsystem: handbook
status: complete
tags: [editor-md, handbook, word-cap]
key-files:
  modified:
    - EDITOR.md
    - tests/test_editor_handbook.py
    - CLAUDE.md
    - docs/decisions.md
decisions:
  - "EDITOR.md 1,800 to 1,701 words; cap lowered to 1,750"
  - "Taken: all Safe, Tighter and fixes, plus C16, Q1, Q3, Q4. Left: C4, C6, C7, C10, C12, C18, C19, C21 and Q2"
metrics:
  tasks: 3
  commits: 1
actuals:
  tasks: 3
  commits: 1
---

# Quick 261104-pt9: Handbook shortening review of EDITOR.md Summary

EDITOR.md is cut from 1,800 to 1,701 words on the user's word, with the cap lowered to 1,750, on `stage-19-handbook-review`, committed and not pushed or merged.

## What was done

- Task 1 (review and draft) and Task 2 (the user's answer: "paste all plus C16, Q1, Q3, Q4, cap 1,750") came before this run.
- Task 3: applied C16 (one-line-answer example removed, -16), Q1 (steady-and-sharp exception, +8), Q3 (a quarter for "shorter" or "longer" with no number, +18) and Q4 ("slower" means longer shots, +7) to the draft, using the review's exact words. Result 1,701 words, as expected (1,684 - 16 + 8 + 18 + 7).
- The three guards passed on the draft: handbook_problems, recipe_problems and revise_call_problems all empty.
- The draft was copied over EDITOR.md byte for byte.
- Cap lowered to 1,750: MAX_WORDS, its comment and the file's first line in `tests/test_editor_handbook.py`, and the "Settled so far" sentence in CLAUDE.md (earlier raises kept, the lowering added).
- CLAUDE.md "Settled so far": added that a "shorter" or "longer" with no number means a quarter of the length, and that a clip with nothing steady and sharp is left out rather than forced in (Stage 19). "Slower" was not added: it reads as a statement of what the tool does, and speed already waits for Stages 21 and 25.
- docs/decisions.md: one dated line (words before and after, the cap, items taken and left, the guide having no step for this review).

## Tests

`uv run pytest tests/test_editor_handbook.py -q`: 27 passed. No test hard-coded 1800; the cap tests read MAX_WORDS, so no guard was weakened.

## Deviations from Plan

None. Q2 and the eight other Your call cuts were left, as the user said.

## Still to do (for the user)

- Push the branch (needs his word), then the phone test in the review's section 6, then the merge on his word.
- Thin her Project's standing answers (Stage 20, D-04) and change or remove the Reel style sound line: manual steps in her Project.
