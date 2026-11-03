# Phase 7: Stage 19 – Conversation - Context

**Gathered:** 2026-11-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Making a reel becomes a short conversation on her phone: a brief of a few numbered questions asked straight away, one line with a time estimate and then silence, a reply of the video plus two lines and three follow-ups, and follow-ups that change only what she asked for. The code side is one new command, `python -m v2r revise`, which applies one named change to an existing cut list and leaves every other field untouched, plus a `recipe` field in the cut list with its shot-length floors and ceilings in settings.py. The handbook gains a "Talking with her" section in the user's own words. Nothing here chooses moments: a different moment, a different star or a new shot is the chat's Claude editing the list itself.

Not in this phase: music of any kind (Stage 18 closed it: the tool adds no music), saved preferences that answer the brief for good (Stage 21), words on screen and filters (Stage 21), beat matching (Stage 22, in question), long or large files (Stage 23), transcripts (Stage 24).

</domain>

<decisions>
## Implementation Decisions

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The plan and the records
- `docs/field-guide.html` — Stage 19 (section `s19`): what the stage must do, the two Decide boxes, the Fable prompt, the Do-this steps and the Watch-out (a follow-up that starts from scratch is the failure to hunt for). Stage 17's rehearsal prompt is reused for this stage's rehearsals. Read only those stages.
- `CLAUDE.md` — the project rules, the three jobs, "Settled so far" (Stage 17's defaults and two questions; Stage 18's no-music decision).
- `docs/decisions.md` — the Stage 17 and Stage 18 lines (what the handbook already assumes).
- `docs/phone-limits.md` — rows 15 to 18, the timings behind the estimate rule (D-03).
- `.planning/phases/05-stage-17-editor-s-handbook/05-CONTEXT.md` — D-05 (defaults), D-06 (the two questions this phase folds into the brief), D-08 (EDITOR.md is the user's text; the draft-and-approve routine), D-10 (rehearsals in fresh sessions), D-13 (no editing judgement in Python).
- `.planning/phases/04-stage-16-cut-list-and-renderer/04-CONTEXT.md` — D-01 (frame rounding), D-03 (canvas must match the clips' shape), D-05 (segments), D-09 (cover by segment and second), D-12 (naming the subject steers the reel), D-13 (attach order only names clips), D-17 (a silent reel is allowed).

### The code revise builds on
- `schema/cutlist.schema.json` — the list's rulebook; `recipe` is added here.
- `v2r/render/check.py` — `read_cutlist`, `read_manifest`, `segment_lengths`, `working_seconds`, the problem and note sentences, `report`; revise reuses its reading and reporting and adds the recipe note.
- `v2r/settings.py` — `MIN_REEL_SECONDS`, `MAX_SEGMENTS`, `PHOTO_SECONDS`, `OUTPUT_FPS`; the recipe floors and ceilings join them.
- `v2r/__main__.py` — the argparse layout: `check`, `match` and `render` share one loop that adds `[CUTLIST]` and `--work`; `revise` joins that pattern.
- `v2r/render/__init__.py` — `new_path` numbers output files; revise's numbering follows the same habit.
- `tests/cutlists.py`, `tests/test_cutlist_check.py`, `tests/test_editor_handbook.py` — fixture lists, the checker's test style, and the handbook guards (`MAX_WORDS`, every command named exists, no Mac-only switches).
- `EDITOR.md` — the handbook as it stands (1,309 words): "Before editing", the steps, "Sound", "Before sending", "When things go wrong".

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `v2r/render/check.py`: reads a list defensively (size cap, digit cap, three-hour cap), reads the manifest, computes segment lengths and working seconds, and turns problems into one plain sentence each; revise should read and report through the same functions rather than parse JSON afresh.
- `v2r/__main__.py`: the loop that registers `check`, `match` and `render` with `[CUTLIST]` and `--work FOLDER` is the slot for `revise`.
- `v2r/render/__init__.py::new_path`: the numbering habit for new files in `work/`.
- `tests/cutlists.py` and `tests/media.py`: ready-made valid lists and generated clips; the "only its own fields change" proofs can diff whole lists built from them.
- `tests/test_editor_handbook.py`: the guards (word cap, every named command exists, no `--work` or `--no-size-limit`) extend to `revise` and to the recipe numbers.

### Established Patterns
- Every number lives in settings.py; every refusal is one plain sentence; a note never blocks a build; every output is a new file; originals are never modified.
- Code decides nothing about the edit: look measures, the chat's Claude writes the list, render builds it. revise is a mechanical transform the chat's Claude invokes with its own judgement spelled out in the arguments.
- Times are seconds on a working copy and round to whole frames at 30 a second (nearest, half up).
- The handbook is the user's text, held under a word cap by a test; drafts live in the phase folder, never pasted into EDITOR.md without his word.

### Integration Points
- `schema/cutlist.schema.json` (+ `recipe`), `v2r/render/check.py` (recipe note, assumed-Lively note), `v2r/settings.py` (recipe floors and ceilings), `v2r/__main__.py` (the `revise` command), a new `v2r/render/revise.py` or `v2r/revise.py`, `README.md` (command row), `EDITOR.md` (the user's new section), `.planning/REQUIREMENTS.md` (CONV wording), `docs/decisions.md` and `CLAUDE.md` (the closed Decide box).

</code_context>

<specifics>
## Specific Ideas

- The user's prompt, in his words, is the brief for this stage: the brief's four questions with the first two already asked since Stage 17; one line and a time estimate, then silence; the reply of the video, at most two lines, three follow-ups; "the list of follow-ups and, for each, exactly which fields of the existing cut list change"; "describing clips by what is in them, never by letter"; "python -m v2r revise ... leaves every other field untouched"; "Tests must prove that each revision changes only its own fields."
- "Trim the weakest shots first" (the user's own answer): the chat's Claude names them; code never scores weakness.
- The guide's check after "shorter": the shots should be the same ones, just less of them.
- The guide's Watch-out: she says "a bit shorter" and gets a different reel, new shots and new order; the cause is always re-running the whole handbook instead of changing the existing list. Step 4 of the Do-this list (compare the cut lists before and after) is the check.
- The time rule's evidence: seven files took nine to eleven minutes on 2026-11-02 (about three of them converting); a tall Stage 16 reel took about four minutes and a wide one about five.

</specifics>

<deferred>
## Deferred Ideas

- Saved preferences that answer parts of the brief for good, so it shrinks to what changes every time — Stage 21.
- "Taste test" and "update my profile" — Stage 21.
- Cutting to a steady pulse or to a song's beat — Stage 22, which is in question since Stage 18 dropped music from the tool.
- Picking a different moment, a different star or a new shot automatically — never: that is the chat's Claude's judgement, by design.
- A fresh chat suggested for a new set of clips is a handbook line in this phase (D-17), not a feature.

</deferred>

---

*Phase: 07-stage-19-conversation*
*Context gathered: 2026-11-03*
