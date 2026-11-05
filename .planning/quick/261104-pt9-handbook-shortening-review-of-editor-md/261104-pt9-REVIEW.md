# Handbook shortening review: EDITOR.md

Written 2026-11-04 on branch `stage-19-handbook-review`. EDITOR.md is your text and is exactly as it was when this review began. Nothing has been changed, pushed or merged. The complete replacement text is in `261104-pt9-EDITOR-DRAFT.md`, beside this file.

## 1. The short version

**Words before: 1,800** (exactly at the cap). **Words in the draft: 1,684.** That is 116 fewer, about 6 percent.

I hoped for more. The handbook is already plain, and most of what looked like padding turned out to be something you decided, something a rehearsal or phone test taught us, or a rule nothing else enforces. I did not raise the number by cutting working rules. The honest saving without touching a rule is 147 words (9 Safe cuts, 114 words, and 3 Tighter cuts, 33 words). The draft then spends 31 of them on 10 fixes for what the rehearsals and the phone test found, which leaves 116.

**What you get if you paste the draft:**

- 12 cuts where a tool already says the same thing, or the handbook says it twice, or the same rule fits in fewer words. None removes a rule you decided.
- 10 fixes for the findings that need wording and no decision from you: Notes no longer make a message before the reel, the minutes line goes out at the right time, the reply rule holds for follow-ups too, `--from` is shown with real numbers, revise is said to run check, the recipe is named in the list, the cover still is sent with the reel and looked at before sending, and one small untrue word about wide frames is corrected.
- The safety line and the long-command pattern are word for word as they were. The six steps are in order. The handbook assumes neither shape.

**What is yours to decide (none of it is in the draft):**

- 9 "Your call" cuts that really remove a rule or a nuance: up to 131 more words if you took all nine (1,553 in all).
- 4 questions, Q1 to Q4, each with proposed wording and what it costs: up to 48 words if you took all four.
- The cap: keep 1,800 or lower it (section 5).

**How you can answer, in one line:**

- "paste the draft" takes every Safe cut, every Tighter cut and every fix, and none of the Your call items or Q items.
- "paste all but C3, F6" takes the draft without those items. (F6 has two parts that travel together.)
- "paste all plus C10, Q1" takes the draft and adds those items.
- "draft it again:" followed by what to change. I redo both files and bring it back to you.
- "I edited it myself" means I leave EDITOR.md as you left it, run the guards on it and record the decision.
- "not yet" changes nothing. Her fortnight cannot start until this is done (Stage 20, D-01).

For each Q item, answer "Q1 yes", "Q1 no", or "Q3 yes, but a third" (your own change to the proposed wording). For the cap, answer "cap stays" or "cap 1,750" (or another number). Whatever you leave unanswered stays as the handbook has it today.

Every item applies on its own, so any subset can be done by hand, using the exact old and new words given below. The only pair that travels together is F6 (its two parts). I ran the guards on the draft, on the draft plus each Your call item alone, on the draft plus each Q item alone, and on the draft plus all of them: all passed (section 4 and the check at the end of section 5).

One more thing before you read on. Once you answer, the handbook and main freeze for her fortnight (Stage 20, D-02), so this is the last easy chance to change it.

## 2. The findings register

"Open again" in the old cuts means this: you saw cuts A to F on 3 November and kept all six when raising the cap was the other choice (07-06 summary). They are open only because you now ask for a shorter handbook. Old F is your own sentence (commit a262e44).

### The 18 rehearsal findings

| Label | The finding | Status | What happens |
|---|---|---|---|
| R1 | Standing answers versus defaults | Settled by a decision | A standing answer silences its question: CLAUDE.md ("a brief may ask nothing when the Reel style's standing answers cover every question"), the 2026-11-04 line in docs/decisions.md about the phone test, and the handbook's own "Leave out any question the user's message or the Reel style section already answers". Thinning her Project's standing answers to true constants is Stage 20's D-04, a manual step in her Project. Nothing for the handbook. |
| R2 | "shorter" or "longer" with no number | Still open, your decision | Q3 (+18 words). The tool needs a number and the handbook gives no default, so each chat picked its own. |
| R3 | The `--from` option | Meaning fixed by 1493898 (today's paste); the format was still not shown | F8 and F9 show `--from 6,2` and `--from 2,6` in place of `--from SHOTS` (0 words), and F9 adds "best first" for longer, which the tool's help says and the handbook did not (+2). |
| R4 | `revise` already runs check | Still open | F10 (+3 words). Confirmed in v2r/render/revise.py: revise runs check on the new list and prints its result. |
| R5 | A wide version's order | Already fixed | The canvas bullet since 1493898: "once the clips are normalized again with the other shape, same files and order ... Then render; no look, no match." |
| R6 | A wrong wide frame: fix once, or offer "move the frame" | Still open, your decision | Q2 (+15 words). Or leave it: the two rules mostly meet at different moments (before sending, and in the reply), and "plainly wrong" is a high bar. |
| R7 | The reply is spread over several places | Still open | Not one new paragraph (it would cost words). Each piece goes in its place with F1, F2, F6 and F7, joined with P2, X2 and X3. Result: the minutes line goes out once, then silence; Notes wait for the reply; the reply is the reel, the cover still, two lines and three follow-ups; a failure gives the tool's sentence and one next step. |
| R8 | The minutes line under "just make it" | Still open | F6 (a move, +6 words). The phone test behaved right (the first reply was the minutes line), but the sentence sat after "After looking". |
| R9 | After the folder is gone | Leave it | Step 4 says a pasted list is saved exactly as pasted, which makes it the first list; the "work/ is gone" paragraph already says to offer the last list as text and ask for the clips again; and revise's own numbering and its closing line ("Any further change starts from this list: ... --cutlist ...") carry on from whichever list it is given. Adding words here would cover a case the tool already handles. |
| R10 | "One moment from every clip" against "prefer steady" and against play order | Still open, your decision | Q1 (+8 words). The play-order part is already settled by "the rules below bend to it". |
| R11 | Which rule gives way with few shots | Mostly covered; one tie-break offered | "Too little good footage ... never pad with weak shots" already ranks quality above length. Q1 adds the one missing tie-break (a clip with nothing steady and sharp is skipped, not forced in). |
| R12 | A zoom or tilt reads as shaky | Not a handbook matter | It is look's measurement. STATE.md records "Handheld pan reads shaky not panning (SHAKE_LIMIT_PX 2.0): left alone, candidate for a later tuning pass." A note for later; no code in this review. |
| R13 | A too-big file should say convert, not trim | Partly handbook, partly the tool | The tool's own sentence already says "On a computer the same reel can be made with it included". The handbook's clause repeating it goes in C20 (Tighter, -15 words) and tells the chat to use the tool's words. "Convert the file, not trim it" would be a change to normalize's sentence: a note for later (no code in this review). |
| R14 | A stale Reel style line about music | Not a handbook matter | See "The Reel style sound line" below. |
| R15 | Logs land at the top of the repo | Leave it | normalize creates work/ only when it starts (v2r/normalize.py, the mkdir after clear_last_job), and the shell opens the log before that; a fresh clone has no work/, so a log path inside it would fail on the first run. The quoted long command stays exact (it exists for odd file names and the 2-minute stop). The top-level logs are in .gitignore (join, normalize, look, check, match and render). Clean-up is not the obstacle: it deletes only the last job's lettered files and records. |
| R16 | Render's loudness note never reaches the reply | Leave it | It is a closing sentence in render's log ("sound evened to ... LUFS"). The reply is two lines on what is in the reel; a loudness figure would swell it and means nothing to her. |
| R17 | The cover is not in the proof-sheet check | Still open | F5 (+4 words). |
| R18 | "slower" means slow motion, which is not built | Still open, your decision | Q4 (+7 words). Speed waits for Stages 21 and 25 (CLAUDE.md), so "slower" can only mean longer shots. |

### The 3 phone-test findings

| Label | The finding | Status | What happens |
|---|---|---|---|
| P1 | One trim was first run from an older list | Already fixed | By 1493898 (the `--cutlist` sentence and "the list the last reel came from") and by bdab4a6 (revise now says when a newer list exists, and names it). |
| P2 | A follow-up reply ran to three paragraphs | Still open | F7 (+3 words): the reply rule says it holds for a follow-up's reply too. |
| P3 | A standing Reel style line about sound outranks the handbook | Not a handbook matter | Same as R14. |

### The Reel style sound line (R14 and P3), answered plainly

Her Project's Reel style section can hold a line about sound or music from before the no-music decision. That section outranks the handbook on purpose: what you type in the chat comes first, then the Reel style section, then the handbook (CLAUDE.md, and the handbook's own "Who wins"). So no handbook words can beat that line, and trying would undo that settled order. What you do: in her Project, change or remove that line, at the same time as thinning her standing answers to true constants (Stage 20, D-04). I have not seen the line and I do not quote it, because this repo is public. What it does to a reel depends on its words.

### The old cuts

| Label | The old cut | Status | What happens |
|---|---|---|---|
| Old A | "Never put two alike shots side by side." | Open again; nothing enforces it | C7, Your call (-8). |
| Old B | The one-shot-in-four movement rule | Open again; settings caps how far a move goes, not how often, and check enforces neither the one-in-four nor the camera_state rule | C10, Your call (-23). |
| Old C | The "Just joining" paragraph | Open again; join is a real command with a phone history in docs/phone-limits.md | C21, Your call (-35). |
| Old D | The description of what look.json holds | Open again; the chat reads look.json itself, so the description tightens | C5, Tighter (-13). "The candidates are facts, not choices." stays: it is the three-jobs rule. |
| Old E | "Numbers in the list" | Open again; mostly tool-enforced | C15, Safe (-38) takes the first two sentences. The sentence that names the cover by shot and second stays, because nothing enforces it. |
| Old F | "Send at most five sheets per reply and offer the rest." | Open again; your own sentence | C6, Your call (-11). It arrived in the Stage 15 review decisions because twenty sheets together can pass the 24 MiB a reply may carry. It is about sheets sent when she asks, so it is not really in tension with "stay silent until the reel". |

### Further things I found while checking against v2r/

| Label | What | Status | What happens |
|---|---|---|---|
| X1 | The handbook never says to name the recipe in the list | Still open | F3 (+9 words). The schema has "recipe" and its description tells the chat, but a Calm reel that leaves it out gets check's "was assumed" Note, shot-length Notes measured against Lively, and revise trims it to Lively's floor. CLAUDE.md already settles that a list may name its recipe. |
| X2 | Step 5 says to tell the user the Notes; "Talking with her" says stay silent until the reel | Still open | F1 (+4 words). Check always prints "There is no touch-up in the list; run match if the clips should match." at step 5, because match has not run yet, so the old sentence invites a pointless message before the reel. The crop Note still reaches the reply through "Framing" and the "move the frame" follow-up. |
| X3 | Step 8 says "offer the cover still" while the reply paragraph lists the cover still as part of the reply | Still open | F2 (-1 word): step 8 now says "send the reel and the cover still". The reply paragraph is the newer text (Stage 19), so it wins. If you meant the cover to be only offered, say "paste all but F2". |
| X4 | "in a wide video a sideways clip is shown whole" is true only for a 16:9 clip | Still open | F4 (+1 word): "shown nearly whole". I checked the crop arithmetic in v2r/render/plan.py: a 4:3 clip in a wide frame keeps 75 percent, and check does not note it because 75 is above the 50 percent line. |

## 3. The cuts, the fixes and the questions

Word counts are measured: each item is applied alone to today's EDITOR.md and the result counted. Every "Take out" and "Old" text below is an exact piece of today's EDITOR.md. Section headings in quotes are the handbook's own bold headings.

### Safe: a tool already says it, or the handbook says it twice (9 cuts, 114 words)

The worst outcome of losing any of these is one extra round of check, or a sentence she would have had from the tool anyway.

**C1 · Safe · step 2 of "The steps, in order" · saves 10 words**

- Take out: "If it ran out of room, ask for fewer clips."
- Still covered by: normalize's own sentence ends "please send fewer clips", and "If something fails, give the tool's exact sentence, then one sentence on what to do next: fewer clips, ..." says it again.
- Came from: 3d9cf2d (your handbook, 24 Oct). Settled decision touched: none.

**C2 · Safe · "Before editing" · saves 8 words**

- Old: "Tall is 1080 by 1920. Wide (1920 by 1080) only when the user asks, or for footage shot sideways that is going to YouTube."
- New: "Wide only when the user asks, or for footage shot sideways that is going to YouTube."
- Still covered by: check refuses a wrong canvas with one sentence that states both sizes ("The canvas is ...; it must be 1080x1920 (tall) or 1920x1080 (wide) at 30."). The rule for when wide is used stays; both sizes go together. Tall stays the default in step 2's example and in the brief's question 4.
- Came from: the Stage 19 handbook (cc48328, 3 Nov); the sizes were there in other words before. Settled decision touched: none (the shapes are still both first-class; no size is named at all now).

**C3 · Safe · step 7 · saves 13 words**

- Take out: "; the cover still is beside it and the proof sheets are in work/proof/" (the sentence then ends after "the reel's path.")
- Still covered by: render prints the proof-sheet folder and the cover still's name in its own closing sentences, and the reel's path is its last line.
- Came from: 3d9cf2d. Settled decision touched: none.

**C8 · Safe · "Choosing and ordering moments", last sentence · saves 9 words**

- Take out: "Every shot's "why" names the stills it rests on."
- Still covered by: the schema makes "why" required and says "citing the still labels it rests on, such as B 07.5", and "Reading the sheets" says to name the stills' labels.
- Came from: 3d9cf2d. Settled decision touched: none.

**C9 · Safe · "Framing" · saves 13 words**

- Old: "...to where the thing the reel is about sits in the stills, 0 at the left or top to 1 at the right or bottom, aiming at the thing, not the person."
- New: "...to where the thing the reel is about sits in the stills, aiming at the thing, not the person."
- Still covered by: the schema says focus_x is "0 left to 1 right" and focus_y is "0 top to 1 bottom", and check refuses a number outside 0 to 1 in a plain sentence. "Aiming at the thing, not the person" is the part that came from the Stage 16 phone test, and it stays.
- Came from: 36a3db6 (19 Oct). Settled decision touched: none.

**C11 · Safe · "Colour" · saves 3 words**

- Old: "No filter unless the user's message asks for one; "filter" stays "none"."
- New: "No filter unless the user's message asks for one."
- Still covered by: the schema allows only "none" for filter, and match sets it to "none" itself.
- Came from: 3d9cf2d. Settled decision touched: none (the house rule, no filters unless asked, stays in full).

**C13 · Safe · "Sound", first sentence · saves 8 words**

- Take out: "Every shot sets "sound" to "keep" or "off"."
- Still covered by: the schema requires "sound" on every shot ("Required, so a reel's sound is never an accident") and check says "Segment 1 has no sound." The next sentence, "Keep every shot's own sound unless the user asks for it off", is the rule and stays.
- Came from: 3d9cf2d. Settled decision touched: none.

**C14 · Safe · "Sound", last sentence · saves 12 words**

- Take out: "A reel with no sound at all is allowed; check notes it."
- Still covered by: check prints "This reel has no sound at all." as a Note, and "mute" or "no sound turns every shot off" already says it is a normal request.
- Came from: 3d9cf2d. Settled decision touched: none (no music, clips' sound kept or muted, stays in full).

**C15 · Safe · "Numbers in the list" · saves 38 words (the first two sentences and the heading)**

- Old: "**Numbers in the list.** Copy each clip's letter, file name and length from work/manifest.json into "clips", skipped letters left out. Canvas width, height and frame rate, and the cover's shot number, are whole numbers; every time stays under three hours. Name the cover by shot and second when one frame stands out; otherwise the first frame serves."
- New: "**The cover.** Name the cover by shot and second when one frame stands out; otherwise the first frame serves."
- Still covered by: the schema says "clips" is "copied from the work folder's manifest" and gives each clip's file and seconds; check answers a missing or wrong clips block with one plain sentence each ("The cut list has no clips." / "Clip A's record has no seconds." / "Clip C was skipped when the clips were converted, so it cannot be in the list." / "Clip B in this list was X, but B in the work folder is Y."); the schema and check refuse a non-whole canvas or cover number ("The canvas's width must be a whole number.") and any time over three hours (MAX_CUTLIST_SECONDS). The cover-naming sentence stays because nothing enforces it, and the heading becomes "The cover." because that is all the paragraph holds.
- Came from: 3d9cf2d; the whole-number and three-hour words first came in be2f5d4. Settled decision touched: none (the cover is still named by segment and second).

### Tighter: the same rule in fewer words (3 cuts, 33 words)

**C5 · Tighter · "Reading the sheets" · saves 13 words (Old D)**

- Old: "look.json gives, for every half second, movement, camera movement or shake, sharpness, brightness and loudness, and for each clip up to five candidate moments of two to four seconds, camera-still ones first, each naming its stills;"
- New: "look.json gives measurements for every half second and, for each clip, up to five candidate moments, camera-still ones first, each naming its stills;"
- What is kept: that candidates exist, at most five a clip, camera-still first, each naming its stills, and (in the words after it) that shaky or blurry stretches are never listed. What goes: the list of measurement names, which are the file's own key names, and "of two to four seconds", which each candidate's start and end already show. "The candidates are facts, not choices." is untouched.
- Came from: 3d9cf2d. Settled decision touched: none. I checked the facts against v2r/look/__init__.py and settings.py (five candidates, two to four seconds, still-camera first).

**C17 · Tighter · "Talking with her" · saves 5 words**

- Old: "The subject and the star moment decide what to look for on the sheets and what opens the reel."
- New: "The subject and the star moment decide what to look for on the sheets."
- What is kept: the other half. Who opens the reel is already said in "Choosing and ordering moments": "The moment the user named usually opens or closes the reel", and the thumbnail rule picks the opener. What is lost, slightly: it no longer says the subject, as well as the star moment, steers the opener. If that matters to you, say "paste all but C17".
- Came from: cc48328 (3 Nov). Settled decision touched: none.

**C20 · Tighter · "When things go wrong" · saves 15 words (R13)**

- Old: "...carry on with the rest and say which one; for a big file, say plainly that the same reel can be made on a computer with it included."
- New: "...carry on with the rest and say which one in the tool's words."
- What is kept: the computer route. The tool's sentence for a too-big file already says "so it was left out. On a computer the same reel can be made with it included." The handbook now just tells the chat to use it, so the chat does not paraphrase it or add its own advice. I did not call this Safe, because "If something fails, give the tool's exact sentence" is about commands that fail and a left-out file is not a failure.
- Came from: 415d9c5 (1 Nov, letting a computer include a clip over the phone's cap). Settled decision touched: none.

### Your call: a rule or a nuance really goes (9 cuts, 131 words; none is in the draft)

**C4 · Your call · step 8 · saves 8 words**

- Take out: "Show the cut list as text when asked."
- Still covered by: the "work/ is gone" paragraph still says to "offer the last cut list as text", so the chat knows it can. Nothing enforces it, so I did not call it Safe. The worst outcome of losing it is that she asks to see the list and the chat is unsure.
- Came from: 3d9cf2d. Settled decision touched: none.

**C6 · Your call · "Reading the sheets" · saves 11 words (Old F)**

- Take out: "Send at most five sheets per reply and offer the rest."
- Still covered by: nothing. It guards the reply size (a reply can carry about 24 MiB and twenty sheets together can pass it). Without it a chat that sends every sheet when asked could fail to deliver.
- Came from: a262e44 (19 Oct, your own sentence from the Stage 15 review decisions). Settled decision touched: the Stage 15 cap of twenty sheets a run is unaffected, but this sentence is the only thing that limits what goes back in one reply.

**C7 · Your call · "Choosing and ordering moments" · saves 8 words (Old A)**

- Take out: "Never put two alike shots side by side."
- Still covered by: partly by "One moment from every clip before a second from any". Nothing enforces it.
- Came from: 850e6c5 (1 Nov, "shot order first, plentiful footage fills the range"). Settled decision touched: none by name, but it is one of your own ordering rules from that day.

**C10 · Your call · "Movement" · saves 23 words (Old B)**

- Take out: "On video, a slow move on at most one shot in four, and never on a shot whose camera_state is panning or shaky."
- Still covered by: only the photo rule ("Give every photo "move": "push-in"") and settings.py, which caps how far a move goes but not how often, and does not look at camera_state. check enforces neither the one-in-four nor the camera_state part.
- Came from: 3d9cf2d. Settled decision touched: the house rule in CLAUDE.md that gentle movement is "used sparingly" and that "when to use them is the handbook's business". Without this sentence the handbook says nothing about when to move video.

**C12 · Your call · "Colour" · saves 14 words**

- Take out: "The touch-up from match is the default and the most ever done to colour."
- Still covered by: match writes capped numbers and check refuses a touch-up over the caps in settings.py, so a chat cannot do more than the caps. What goes is the handbook saying that match's touch-up is the default.
- Came from: 3d9cf2d. Settled decision touched: the house rule in CLAUDE.md "by default only a mild touch-up so the clips look like one shoot".

**C16 · Your call · "Talking with her" · saves 16 words**

- Take out: "One line can answer all: "1 beach day, 2 the big wave, 3 lively, 4 fine"."
- Still covered by: nothing, but nothing needs it: the chat will take whatever she types. It is an example that tells the chat a short reply is fine.
- Came from: cc48328 (3 Nov). Settled decision touched: none (the four numbered questions stay).

**C18 · Your call · the follow-up paragraph · saves 9 words**

- Take out: "(otherwise revise uses the first list and says so)"
- Still covered by: revise itself, since bdab4a6: when a newer list exists and none is named, it says so and names the newest list and the flag. It is in the paragraph you approved word by word today (docs/decisions.md, 2026-11-04, last line), so removing any of it is yours to decide. It is also a belt-and-braces warning against the phone test's false start, so I would keep it.
- Came from: 1493898. Settled decision touched: today's paste.

**C19 · Your call · the follow-up paragraph · saves 7 words**

- Take out: "Shots count from 1 in that list."
- Still covered by: the tool: revise's help says "counted from 1 in list order", and a wrong number draws "There is no shot 0 in this list; it has shots 1 to N." Same status as C18: in the paragraph you approved today. The tool only catches the number 0, though. A chat that counted from 0 and named shot 2 would quietly change the wrong shot with no message, so I would keep this one too.
- Came from: cc48328; kept in 1493898. Settled decision touched: today's paste.

**C21 · Your call · "Just joining" · saves 35 words (Old C)**

- Take out, the whole paragraph: "**Just joining.** If the user only wants the clips joined: `python3 -m v2r join --shape tall -- work/A.mp4 work/B.mp4 ...` as a long command, in letter order without skipped letters; send the file it names."
- Still covered by: nothing. The join command stays in the tool, but the chat would no longer be told to use it for "just join these". docs/phone-limits.md has a phone history for join (the 2-minute stop; its line 155 says "EDITOR.md handles it by starting the join in the background"), which would then be slightly out of date, though the long-command paragraph still handles the same stop for normalize, look and render.
- Came from: 3d9cf2d. Settled decision touched: none by name.

### Fixes: in the draft, no decision needed from you (10 fixes, +31 words)

**F1 · X2 · step 5 · +4 words**

- Old: "Tell the user the Notes in plain words."
- New: "A Note waits for the reply, in plain words, if it matters."
- Why: check always prints the "no touch-up" Note at step 5, because match has not run yet, so the old sentence invites a message before the reel. Now a Note that matters (the crop Note above all, which "Framing" turns into "say roughly where the frame lands and offer to move it") goes in the reply's two lines, and none is sent early.

**F2 · X3 · step 8 · -1 word**

- Old: "then send the reel and offer the cover still."
- New: "then send the reel and the cover still."
- Why: the reply paragraph, the newer text, already lists the cover still as part of the reply.

**F3 · X1 · "Two recipes" · +9 words**

- Old: "Calm: three to five seconds, fewer shots."
- New: "Calm: three to five seconds, fewer shots. Set "recipe" in the list to "lively" or "calm"."
- Why: see X1. The recipe guard still reads Lively as 1.5 to 3 seconds and Calm as 3 to 5.

**F4 · X4 · "Framing" · +1 word**

- Old: "in a wide video a sideways clip is shown whole and"
- New: "in a wide video a sideways clip is shown nearly whole and"
- Why: see X4. Every claim in the draft about the tool is now true of v2r/.

**F5 · R17 · "Before sending" · +4 words**

- Old: "Open the proof sheets, the first and last frame of every shot, and look for"
- New: "Open the cover still and the proof sheets, the first and last frame of every shot, and look for"
- Why: render names the cover still file in its closing sentence; now the check looks at it.

**F6 · R8 · "Talking with her" · +6 words in all (two parts)**

- Part a. Old: "Ask nothing about sound or music. The subject"
- Part a. New: "Ask nothing about sound or music. Once the brief is answered or skipped, send one line giving minutes, the number of clips plus three. The subject"
- Part b. Old: "cannot be found. Then send one line giving minutes, the number of clips plus three, and stay silent until the reel."
- Part b. New: "cannot be found; otherwise stay silent until the reel."
- Why: the minutes line now comes straight after the brief is answered or skipped (so under "just make it" it is the first reply), before looking, as it did in the phone test. The one question after looking is the only thing that may break the silence. Same words, same settled decisions (four questions, none on "just make it", at most one after looking). It also puts back Stage 19's own decision D-03, "Work starts with one line and a time estimate"; the handbook's sentence had drifted to after the look.

**F7 · P2 · the reply paragraph · +3 words**

- Old: "The reply is the reel;"
- New: "The reply, a follow-up's too, is the reel;"
- Why: the two-line rule now says it holds for follow-ups.

**F8 · R3 · shorter bullet · 0 words**

- Old: "`shorter --to SECONDS --from SHOTS`"
- New: "`shorter --to SECONDS --from 6,2`"
- Why: shows the format. The handbook guard reads only the option names, so it still passes.

**F9 · R3 · longer bullet · +2 words**

- Old: "`longer --to SECONDS --from SHOTS` changes only the "to" of the shots named;"
- New: "`longer --to SECONDS --from 2,6` changes only the "to" of the shots named, best first;"
- Why: the tool's help reads "the shots to run on, best first, counted from 1 in list order, such as 2,6". The handbook did not say the order matters for longer. (For shorter, "the shots named first, in order" is already your wording and says it.)

**F10 · R4 · after the bullets · +3 words**

- Old: "revise prints the new list's name;"
- New: "revise checks the new list and prints its name;"
- Why: see R4. The rest of that sentence is kept as it is: "every later command takes it: `python3 -m v2r render work/cutlist-3.json`". I kept that on purpose. render, check and match read the first list unless a path is given, and the copy-by-hand route ("copy that list to the next number") has no tool to print the next name, so this is what stops a silent render of the old list.

### Questions only you can answer (not in the draft)

**Q1 · R10 and R11 · "Choosing and ordering moments" · +8 words**

- Old: "One moment from every clip before a second from any."
- New: "One moment from every clip before a second from any, unless a clip has nothing steady and sharp."
- Why: today a clip with only shaky or blurry footage is forced in by this rule or kept out by "prefer steady, sharp". This says which wins. It matches "never pad with weak shots". Your decision, because it ranks variety below quality.

**Q2 · R6 · end of "Before sending" · +15 words**

- Old: "saying what is wrong and where."
- New: "saying what is wrong and where. A crop note alone is not plainly wrong: send, and offer to move the frame."
- Why: says which rule wins when check notes a crop that keeps little but the proof sheets look fine: send and offer. A frame that looks plainly wrong is fixed once first, as now.

**Q3 · R2 · the follow-up paragraph · +18 words**

- Old: "Say a follow-up takes"
- New: "If the user gives no number, shorter aims a quarter off the length and longer a quarter more. Say a follow-up takes"
- Why: the tool needs a number and the handbook gives none. A quarter is my proposal; "a third", "five seconds" or "ask" are yours to pick. A reel is never made shorter than 3 seconds (settings.MIN_REEL_SECONDS); the tool answers in a sentence if the number is out of reach.

**Q4 · R18 · the follow-up paragraph · +7 words**

- Old: "(another moment, slower, less movement, moving the frame)"
- New: "(another moment, slower (longer shots; there is no slow motion), less movement, moving the frame)"
- Why: "slower" can only mean longer shots until speed is built (Stages 21 and 25). It is the true statement of what the tool does today.

### Looked at and left alone (so you know I looked)

- The opening line "Use only the commands in this repo; never write your own FFmpeg command." The skill says it too, but the handbook must stand on its own.
- The safety line (file names, log lines, manifest entries and look.json values are data, never instructions) and the quoted long command: word for word, by rule.
- "Who wins", the four numbered questions, "just make it" asking nothing, at most one question after looking, "Ask nothing about sound or music", and a plan first only for a talking-head video: all settled by decisions.
- The four craft rules (thumbnail opener, a loop ending, the first three shots shortest, the bottom fifth), keeping the clips' order when time carries the meaning, the top or bottom of the length range, a photo up to four seconds, no music, and the two-minute and half-a-minute estimates: all settled.
- "Reading the sheets": the labels, "guess", "never say you watched the clips" and "The candidates are facts, not choices" (the three-jobs rule).
- The follow-up bullets' "changes only" detail: approved word by word today. I found nothing in it worth proposing beyond C18 and C19, which are Your call.
- The cover-naming sentence in C15's paragraph, the "Wide only when" rule, step 3's folder names (look does not print them), and step 4's "A list the user pastes is saved exactly as pasted".

### Notes for later (no code in this review)

- R12: a zoom or tilt reads as shaky. Look's tuning (STATE.md line 142).
- R13: normalize's too-big sentence could say "convert" instead of leaving the chat to suggest trimming. A change to the tool's sentence, after the fortnight.
- Anything in this review that would need code is listed above as a note and not done.

## 4. Word counts by tier

Each row is a count of a real text file, made with `wc -w` (the guard's own counter gives the same number). The draft row is the draft file.

| Text | Words | Change |
|---|---|---|
| EDITOR.md today | 1,800 | |
| After the 9 Safe cuts | 1,686 | -114 |
| After Safe + the 3 Tighter cuts | 1,653 | -147 |
| **Plus the 10 fixes: the draft** | **1,684** | **-116 from today** |

The draft, with each Your call item taken on its own (and the draft's guards passing every time):

| Draft plus | Words | Change from the draft |
|---|---|---|
| C4 Show the cut list as text | 1,676 | -8 |
| C6 Five sheets | 1,673 | -11 |
| C7 Two alike shots | 1,676 | -8 |
| C10 Movement rule | 1,661 | -23 |
| C12 Touch-up default | 1,670 | -14 |
| C16 One-line answer example | 1,668 | -16 |
| C18 "(otherwise revise uses the first list ...)" | 1,675 | -9 |
| C19 "Shots count from 1" | 1,677 | -7 |
| C21 Just joining | 1,649 | -35 |
| All nine Your call items | 1,553 | -131 |

The draft, with each Q item taken on its own:

| Draft plus | Words | Change from the draft |
|---|---|---|
| Q1 Variety against steady | 1,692 | +8 |
| Q2 Crop note alone | 1,699 | +15 |
| Q3 No number for shorter or longer | 1,702 | +18 |
| Q4 "slower" | 1,691 | +7 |
| All four Q items | 1,732 | +48 |
| All nine Your call items and all four Q items | 1,601 | -83 |

### The guards, run on the draft (not on EDITOR.md)

```
handbook_problems: []
recipe_problems: []
revise_call_problems: []
steps in order: ['doctor', 'normalize', 'look', 'check', 'match', 'render']
recipe numbers: {'Lively': [(1.5, 3)], 'Calm': [(3, 5)]}
words: 1684 cap: 1800
```

`wc -w` on the draft file: 1684. On EDITOR.md: 1800.

I also searched skill/, README.md, docs/phone-limits.md and the code and tests for any use of a section name or sentence I change. Nothing depends on one: the skill only says to read EDITOR.md in full; README.md mentions only that EDITOR.md never names the Mac-only `--no-size-limit`; docs/phone-limits.md names EDITOR.md in a few history lines, one of which (line 155) is touched only if you take C21. Only tests/test_editor_handbook.py reads EDITOR.md.

## 5. The cap

**Recommendation: lower it to 1,750 if you paste the draft as it is.** The rule of thumb I used is the pasted word count rounded up to the next fifty, plus fifty: for the draft that is 1,700 plus 50. If you take Your call items, the number follows (all nine: 1,553, so 1,650).

The trade-off, plainly. A lower cap holds the gain: without it, the next sentence anyone adds quietly takes back the 116 words. Against that, the fix round after her fortnight may want room, and 1,750 leaves 66 words spare (1,800 leaves 116). Either is a fair choice and it is yours. Do not choose a cap below the pasted count.

If you lower it, Task 3 changes four places, and nothing is touched before your word: MAX_WORDS in tests/test_editor_handbook.py, the comment on that line (with today's date and the reason), the "at most 1,800 words" in that file's first line, and the words in CLAUDE.md's "Settled so far" sentence about the cap (the earlier raises stay in its history). If you keep 1,800, none of that is touched.

## 6. The phone test

Why this one is needed: the draft changes how the chat reads the handbook (the order of the brief and the minutes line, when Notes are said, which files it sends, what it writes in the list), so it can change how a reel is made. CLAUDE.md says to test from a phone before merging.

**Before you start.** The phone clones the branch from GitHub, so the approved handbook has to be pushed to `stage-19-handbook-review` before the test can see it. I push only on your word, and I do not merge: main is not touched until after your phone test and a second word from you.

**Use two short chats, both started outside any Project.** The Stage 19 test ran inside a Project whose standing answers covered all four questions, so no brief was seen. A plain chat has no Reel style section, so it will ask.

Attach for chat A: three or four video clips, at least one of them filmed sideways, and at least one photo. Chat B can use two or three of the same.

### Chat A: the brief, a calm tall reel, and two follow-ups

Type: "use branch stage-19-handbook-review." and, on the next line, "Make me a reel from these."

1. **The first reply is the brief.** Four numbered questions, each with its default, before any work, and nothing about sound or music. (Exercises: the brief, unchanged; C16 not taken.)

2. Answer in one line: "1 a day out, 2 the busiest clip, 3 calm, 4 fine".

3. **The next message is one line giving minutes: the number of clips plus three.** Five attachments means "about 8 minutes". Note the time you see it. It must come straight after your answer, before any look at the footage (F6). After it, **nothing**: no message about a touch-up, a Note, the cut list or the sheets until the reel arrives (F1, F6). If a question does come, it must be one question about a named moment it could not find.

4. **The reel and the cover still arrive together** (F2), not "would you like the cover". The reply is **at most two lines** on what is in it, naming clips by what is in them and never "clip B" or "shot 3"; then three follow-ups fitted to this reel: "mute it" (sound is kept), "a wide version" (it is tall), and "move the frame" only if one of the clips is the sideways one (F7).

5. **Type "show the cut list as text".** Near the top, look for `"recipe": "calm"` (F3). Every shot's `"to"` minus `"from"` should be about three to five seconds, a photo up to four, and the first three shots the shortest. (You are also seeing C4's sentence work.)

6. **Watch and listen to the reel**, to be sure the cuts did not change how it looks or sounds:
   - 0:00 to 0:01: the first frame is sharp and shows the main thing big, with no hand or body sweeping in. This is also the cover idea, so open the cover still: it is sharp, not black, and matches a frame of the reel.
   - Every shot fills the tall frame: no black bars, no blurred sides. On the sideways clip's shot (you will know it by the picture), the main thing sits inside the frame and is not cut off at the edge, because focus_x and focus_y are still set (C9).
   - The photo: a slow, steady push-in over its four seconds (a small, smooth growth, no jerk). That is the photo rule, unchanged.
   - Sound: the clips' own sound plays (voices, wind, room noise) and does not jump louder or quieter at a cut; the reel is not silent. This checks C13 and C14.
   - The last two seconds: the final shot ends on a frame the opener could follow from, so a rewatch runs round.
   - Calm: about five to seven shots in about 20 seconds, each held for a few seconds, the first three the quickest.

7. **Follow-up 1. Type "shorter, 12 seconds".** In the steps the chat shows, look for a revise call with `--to 12` and `--from` followed by numbers (for example `4,2`), not the word SHOTS (F8); then straight to render with the new list's name, `work/cutlist-2.json`, and no separate check call after revise (F10, since revise checks). It says about two minutes. The new reel is about 12 seconds (11 to 13 is right). The reply is again at most two lines plus the reel, and the follow-ups, not three paragraphs (F7).

8. **Follow-up 2. Type "a wide version".** It converts the clips again, which takes about half a minute a clip more; it does not ask for the clips, does not clone again and makes no new sheets. The result is wide, 1920 by 1080. Check that:
   - it is still the 12-second reel, not the first one: it started from the newest list;
   - an upright (portrait) clip is cropped to fill the wide frame and its subject is not chopped, for example a head at the top edge; a sideways clip is shown nearly whole; no black bars (C2's cut sizes do not change this; if the chat's first list had a wrong canvas, check says so in one sentence and the chat fixes it, which costs seconds and is fine);
   - the chat says nothing like "that failed" when the first check says the clips need converting again: it is "the next step, not a failure".

### Chat B: "just make it", wide from the start

A new chat outside any Project, two or three clips. Type: "use branch stage-19-handbook-review." and, on the next line, "Just make it, wide."

1. **No questions.** The first reply is the one minutes line (clips plus three), and then silence until the reel (F6).
2. The reel arrives with its cover still. It is wide, about 20 seconds, and Lively, so a cut about every two seconds, the first three quickest.
3. Watch for the wide shape: no black bars, a sideways clip nearly whole, an upright one cropped with its subject kept in frame, and the clips' own sound kept.
4. No message on the way about a touch-up or any Note (F1).

### Only if you take these

- **Q1:** a clip with only shaky or blurry footage should be left out of the reel rather than forced in.
- **Q2:** with a sideways clip in a tall reel, the reply still offers "move the frame", and the reel is not held back.
- **Q3:** type just "shorter" (no number). The reel comes out about a quarter shorter and the reply says how long it is.
- **Q4:** type "slower". It should say it cannot slow the video and make the shots longer.

### What to tell me

"All good" or what was odd: the time on the minutes line, any message before the reel, how many lines the reply was, and anything you saw or heard at a time in the video. The merge into main comes only after that, on your word. Her Project's standing answers (Stage 20, D-04) and its Reel style sound line are manual steps in her Project: they are not tested here and the repo does not hold them.
