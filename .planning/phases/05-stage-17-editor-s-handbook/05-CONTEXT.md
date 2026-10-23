# Phase 5: Stage 17 – Editor's handbook - Context

**Gathered:** 2026-10-24
**Status:** Ready for planning

<domain>
## Phase Boundary

EDITOR.md becomes the complete, plain-words handbook the phone's Claude follows: the steps in order naming each command, how to study the sheets and look.json, rules of craft for choosing and ordering moments, the Lively and Calm recipes, the house rules, the honesty rules, what to do when a file cannot be read or there is too little footage, and the order of authority. Taste leaves the repo: a "Reel style" profile is drafted for each account named in the taste notes and saved in fixtures/, never committed. The rehearsal runs for all five fixture sets, a second profile on one set changes only what the profiles differ in, and she would post three of the five with small changes. Requirements HAND-01 to HAND-05. Not in this phase: the music library (Stage 18), the full brief and the revise command (Stage 19), filters, words on screen and profiles that learn (Stage 21), beats, long files, transcripts, voice-over.

</domain>

<decisions>
## Implementation Decisions

### The handbook (settled by the user's brief, 2026-10-24)
- **D-01:** Make the reel first. A plan is shown before building only for talking-head videos, which is Stage 24's rule. The guide's Decide box "show the plan first, or make the reel first" is closed with its pick.
- **D-02:** Taste lives in a section headed "Reel style" in the instructions of each account's existing Claude Project; the handbook holds craft and house rules only. Order of authority, written into the handbook: what the user types in the chat; then the Reel style section of the chat's standing instructions, with the rest of those instructions read as background on the account; then the handbook and its defaults. The guide's Decide box "where taste lives" is closed with its pick. — **Reversibility:** reversible — the handbook names where to look; another place is one sentence.
- **D-03:** EDITOR.md covers (HAND-01): the steps in order naming the exact command for each (doctor, normalize, look, check, match, render; join only when the user wants the clips joined); how to study the contact sheets and look.json; rules of craft (open on the strongest picture; prefer the steady, sharp candidate stretches; one moment from every clip before a second from any; never two alike shots adjacent; end on a shot that feels finished; stay within a tenth of the length asked; the moment the user named usually opens or closes the reel; attach order is not shot order, Phase 4's D-13); the Lively recipe (shots of 1.5 to 3 s, the default) and Calm (3 to 5 s, fewer shots); the house rules (no filter unless the user asks, match by default; every shot fills the tall frame, sideways clips cropped and never mixed in as widescreen; a wide video keeps sideways footage whole and is wide throughout; a slow move on photos and on at most one video shot in four, never on a shot look.json marks as moving or shaky); the honesty rules (every shot's "why" cites still labels; anything between stills is called a guess; never "I watched your clips"); the proof sheets before sending and fixing the cut list at most once; what to do with an unreadable file (carry on, say which) and too little good footage (shorter, say so, never pad); and that only the repo's commands may be used. Two pages at most, short sentences, no programming terms beyond the command names and one long-command recipe, written so the user can edit it himself.
- **D-04:** "Two pages" is held by a test: EDITOR.md may hold at most 1,200 words (whitespace-split), and the test fails above that. The number lives in the test, not settings.py, because it is a repo rule and settings.py ships to the sandbox. EDITOR.md is 912 words today; the draft folds the four background-command recipes into one "long commands" paragraph to make room for the craft.
- **D-05:** Defaults when the message says nothing: about 20 seconds, tall (1080 by 1920), Lively, no filter, a mild touch-up, no music. Wide (1920 by 1080) only when the user asks, or for footage shot sideways that is going to YouTube.
- **D-06:** Asking before editing, until Stage 19 builds the brief: two questions in one short message, only when the message did not say them: what the reel is about, and which moment is the star. Nothing else is asked; everything else takes the defaults. Stage 19 turns the defaults into its questions.
- **D-07:** Music until Stage 18: a real reel is made without music, every shot's own sound off unless the user asks to keep one or names a sound they want, and the reply says a song can be added in the posting app. If the user asks for music before the library exists, the reply says the library is coming and the reel is still made silent. check's note about a reel with no sound is expected. The test tone stays a test fixture only.
- **D-08:** The handbook draft is reviewed by the user before planning: it is `05-HANDBOOK-DRAFT.md` in this folder (committed; it holds no private content). EDITOR.md itself changes only as the user's text: he edits it, or asks for the draft to be pasted, as he did in Stage 16. No executor edits EDITOR.md on its own initiative; a plan task that touches EDITOR.md is a checkpoint for his word.

### Rehearsals and fixtures
- **D-09:** `normalize` and `look` gain `--work FOLDER` (check, match and render already have it; look already takes a positional folder) so each fixture set rehearses into work/<set>/ and the five reels sit side by side. Mac-only convenience: the handbook keeps plain work/, the phone's sandbox is wiped at the end of every chat, and work/ and fixtures/ stay git-ignored. `normalize --work` clears that folder's last job the same way it clears work/; render keeps "every output is a new file", so old rehearsal reels are deleted by hand.
- **D-10:** The rehearsal (the guide's Stage 17 prompt: act as the phone's Claude handed EDITOR.md and one profile, follow it step by step on one fixture set) runs in a fresh Claude Code session after /clear, never in the orchestrating session, once per fixture set. Five sets exist in fixtures/ (names not recorded here); one is a sideways talking-head set that is always made wide. Then one set is rehearsed a second time with a different profile; the two cut lists are compared as text and both reels watched: they must differ only where the profiles differ (HAND-04). Each rehearsal ends with the list of places where EDITOR.md was unclear or tempting to leave; those feed the user's edits.
- **D-11:** Her scores (1 to 5) and her words go in fixtures/reel-log.md under the Stage 13 ritual; HAND-05 (she would post three of the five with small changes) is a human check recorded there. The phone test on the branch is "make a reel" inside one of her account Projects, which also shows the skill works inside a Project and that the profile is read.
- **D-12:** Profiles: the two taste-notes files name three accounts (one of hers, two of the user's own). One draft per account, headed "Reel style" with the sub-headings Always, Never, Usually and My answers to the brief, saved in fixtures/profiles/ (git-ignored) for pasting into each Project's instructions. Lines the notes do not support are marked [check] for the owner to confirm or strike. Account names never appear in the repo or in .planning. The "reels she admires" lines in both notes files are still blank; the profiles rest on the account lines and the "always does" lines, and the user may fill the blanks before Stage 20.
- **D-13:** No editing judgement in Python (HAND-02): Stage 17's only code is the `--work` plumbing on normalize and look, the word-count test, and (Claude's discretion) a test that every command EDITOR.md names exists in v2r's command line. Nothing in v2r chooses a shot.

### Claude's Discretion
- The exact wording of the handbook within the brief and D-03 to D-07, after the user's review of the draft.
- The word-count test's form, and whether to add the command-names test.
- How `--work` is threaded through normalize's entry point and tests (the out_dir plumbing already exists inside normalize.py).
- Rehearsal folder names (the fixture set's folder name) and how the second-profile comparison is recorded (a text diff of the two cut lists in the reel log entry is enough).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The stage and its rules
- `docs/field-guide.html` — Stage 17 only (`id="s17"` to `id="s18"`): what the handbook must contain, the two Decide boxes (both settled above), the Do-this list with the rehearsal, and the rehearsal prompt. Never edit this file. Also Stage 29's prompt library for the rehearsal and "trace a bad reel" prompts.
- `CLAUDE.md` — the three jobs, the house rules, "I edit EDITOR.md myself", taste never in the repo, the public-repo rules, the merge rule.
- `.planning/REQUIREMENTS.md` — HAND-01 to HAND-05 (the traceability row is a range row; set it to Complete by hand at the end).
- `.planning/ROADMAP.md` §Phase 5 — goal and success criteria.

### What the handbook drives
- `EDITOR.md` — today's ten steps (912 words), including the three Stage 16 steps and the focus-point, whole-number and three-hour sentences the user had pasted; the draft keeps every rule they carry.
- `.planning/phases/05-stage-17-editor-s-handbook/05-HANDBOOK-DRAFT.md` — the proposed handbook text for the user's review (D-08).
- `schema/cutlist.schema.json` — the fields the handbook tells the phone's Claude to write.
- `.planning/phases/04-stage-16-cut-list-and-renderer/04-CONTEXT.md` — D-12 (naming the subject steers the reel), D-13 (attach order only names clips), D-17 (a silent reel is allowed), D-21 (a photo's move is the handbook's line), D-26/D-27 (proof sheets, cover, render's sentences).
- `.planning/phases/04-stage-16-cut-list-and-renderer/04-07-SUMMARY.md` — every sentence and note `check` prints, which the handbook tells Claude to relay in plain words.
- `.planning/phases/04-stage-16-cut-list-and-renderer/04-11-SUMMARY.md` — the phone test and the focus-point finding.
- `skill/vid2reel/SKILL.md` — unchanged: it reads EDITOR.md in full and uses only the repo's commands.
- `docs/phone-limits.md` — the 2-minute command stop and the 30 MiB limit the long-command paragraph answers.

### Private material (read on the Mac only; never copied into the repo or .planning)
- the two taste-notes files in fixtures/ (`fixtures/taste-notes*.txt`) — the accounts and the "always does" lines the profiles rest on.
- `fixtures/profiles/` — the three profile drafts.
- `fixtures/reel-log.md` — where her scores go.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `v2r/__main__.py`: `--work` already parsed for check, match and render (`type=Path, default=None`); add the same option to normalize and look.
- `v2r/normalize.py`: `clear_last_job(out_dir, inputs)`, `write_manifest(out_dir, ...)`, `convert_one(..., out_dir, ...)` already take an output folder; the entry point only needs to pass `--work` through instead of `WORK_DIR`. `normalize(files, shape, out_dir=Path)` is how the Phase 3 experiments wrote elsewhere.
- `v2r/look`: the command already reads `FOLDER/manifest.json` when given a folder.
- `tests/test_render_settings.py`: the guard-test pattern for a constant with a stated meaning; the word-count test follows it in its own file.
- Generated media helpers in `tests/media.py` for any `--work` tests; nothing from fixtures/ is ever used in a test.

### Established Patterns
- One plain sentence per problem from every command; the handbook relays them.
- Every output a new file; originals, working copies and manifest.json never written to.
- Phase branch `stage-17-handbook` created from main by hand before any executor; isolation forced to none; the full suite (1003 tests, 11 to 19 minutes) bounded with run-with-timeout 1800.
- Planning docs use repo-relative paths and never name a person or an account.

### Integration Points
- EDITOR.md is read in full by the skill at the start of every chat; its length is paid for on every reel, which is why D-04 caps it.
- The profiles are pasted by hand into each Project's instructions; nothing in the repo reads them.
- `check`'s notes (crop, silence, no touch-up, photo without a move, fields not built) are the sentences the handbook tells Claude to say back in plain words.

</code_context>

<specifics>
## Specific Ideas

- The user's brief, pasted 2026-10-24, is the specification for the handbook; the draft follows its list in order and keeps the three sentences he had pasted into EDITOR.md during Stage 16 (focus point; whole numbers and the three-hour cap; the music note is replaced by D-07).
- He asked to see the handbook draft and the three profile drafts, and to be told the three sentences Claude is least sure about, before anything is planned. Done at the end of this discuss step; his answers shape the plan.
- "Written so I can edit it myself": headed paragraphs, short sentences, commands named once each.

</specifics>

<deferred>
## Deferred Ideas

- Speed changes, time-lapse blending and a sped-up voice-over (from the user's own taste notes): the cut list accepts `speed` and a voice track with a note; building them is Stages 24 and 25.
- Words on screen (from her notes): Stage 21.
- Music chosen by the period of the home (from her notes): a library tag in Stage 18.
- Profiles that learn from what she changes, "update my profile", the taste test: Stage 21.
- The full brief, follow-ups that edit the existing list, the revise command: Stage 19.
- Render overwriting the previous reel inside a rehearsal folder (raised while discussing rehearsals): not now; "every output is a new file" stays, and old rehearsal reels are deleted by hand.

</deferred>

---

*Phase: 05-stage-17-editor-s-handbook*
*Context gathered: 2026-10-24*
