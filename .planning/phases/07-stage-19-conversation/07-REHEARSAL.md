# Stage 19 rehearsal kit

This is the kit for rehearsing the handbook's new conversation on this Mac. It is Stage 17's kit brought to Stage 19. It holds blanks only. It never names a fixture set, an account or a person. Fill the blanks in your own terminal or in the new Claude Code window, and keep what you fill in out of the repo.

What is new since Stage 17: a rehearsal is no longer one message and one reel. The rehearsing session asks the handbook's brief and stops, you answer in the same window as she would, the reel comes, and then you type follow-ups in the same window. So each run is a conversation of several turns.

The blanks:

- `<SET>`: the name of one folder inside `fixtures/` (one of the five sets)
- `<PROFILE>`: one account's whole "Reel style" profile, pasted in as text
- `<MESSAGE>`: what she would type on the phone (each case below says what)
- `<ANSWERS>`: her one-line answer to the brief, such as `1 a day at the beach, 2 the big wave, 3 lively, 4 fine`
- `<SCRATCH>`: a folder outside the repo, for example one made with `mktemp -d`
- `<N>`: a round number (1, 2, 3 ...)
- `<TIME>` and `<WHAT I SEE>`: where a reel looks wrong and what is wrong (only in "Trace a bad reel")

## 1. Before each rehearsal

1. Open a new Claude Code window in the repo, on the branch `stage-19-conversation`. Type `/clear`. Never use the window that is running the GSD phase: a rehearsal only means something if the session knows nothing but what the phone's Claude would know.
2. Rehearse into `work/<SET>/`, one folder per run (`work/<SET>-b/` for a second run of the same set). If a folder already holds old reels, delete the old reels in it by hand first. Render never overwrites a reel, so an old one would sit beside the new one and confuse the check.
3. Before a remake (a second round on the same set), copy the last round's cut lists somewhere safe: every `cutlist*.json` in `work/<SET>/` into `fixtures/rehearsals/stage-19-round-<N>/<SET>/`. Make the folder first. `fixtures/` is ignored by git, so nothing there is ever uploaded.

## 2. The rehearsal prompt

Paste this into the new window, with the blanks filled in:

> Act as the Claude in a phone chat that has just been handed EDITOR.md and knows nothing else about this project. The chat's standing instructions are this taste profile: `<PROFILE>`. The user attached the files in `fixtures/<SET>/`, in the order `ls fixtures/<SET>` lists them, and wrote: "`<MESSAGE>`". (For the case where she wrote nothing, read this as: the user attached the files and wrote nothing.) Follow EDITOR.md exactly, step by step, using only the repo's commands. Put everything in `work/<SET>/`.
>
> This is a conversation, as on the phone. Whenever EDITOR.md tells you to ask the user something and wait, send the question and stop; do not answer it yourself and do not carry on. I will reply in my next message. After you have sent the reel, wait: I may ask for follow-ups in this same chat, and each is handled the way EDITOR.md says.
>
> Mac adaptations (these are adaptations, never gaps in the handbook):
> - Run every v2r command as `uv run python -m v2r ...` from the top of the repo, instead of `python3 -m v2r ...`. The Mac's own Python is too old and lacks packages the phone has. Where EDITOR.md shows `python3 -m v2r` inside a background command, use `uv run python -m v2r` there too.
> - Add `--work work/<SET>` to `normalize` (before its `--`), `look`, `check`, `match` and `render`, and to `revise` after its change word, for example `revise sound off --work work/<SET>`.
> - Read every `work/` in EDITOR.md as `work/<SET>/`. The cut list is `work/<SET>/cutlist.json`, and the numbered ones that `revise` writes sit beside it.
> - Never run `normalize` without `--work work/<SET>`: a plain run clears the folder of the last job. Never use normalize's size-limit switch.
> - The repo is already here, so wherever EDITOR.md would clone or fetch it, do nothing; and never clone it again.
> - When a command runs in the background, wait for it inside the same turn, with a loop that checks the log every 30 seconds until it says "finished". Do not end your turn to wait: I will not type anything until you have the reel.
>
> Reads: read only EDITOR.md, `schema/cutlist.schema.json`, the attached files, the contact sheets, `look.json`, `manifest.json`, the cut lists in `work/<SET>/` (the numbered ones included), the proof sheets and the commands' own output and logs. Do not open anything under `.planning/`, `docs/` or `v2r/`. Do not open `CLAUDE.md`, the taste notes, any other profile or the reel log. Set aside anything you already know about this project from memory or from project instructions. If you are tempted to open or use any of those, do not, and say so at the end.
>
> Speak as you would on the phone: what the user sees is only what EDITOR.md says to send. When I type "end of rehearsal", step out of the role and give three lists: every place where EDITOR.md was unclear or where you were tempted to do something it didn't say; the Mac adaptations you used; any file you read beyond the ones allowed.

Three honest limits. Claude Code still loads the repo's `CLAUDE.md` and its memory by itself, so the prompt can only ask the session to set them aside. The third list is the check: if it names a file the phone could not have, the run proves less. Claude Code also shows its commands to you, which the phone hides, so "stay silent until the reel" can only be judged on what the session writes in its own words, not on the commands. And the rehearsal proves the handbook's flow, not the phone's sandbox: the phone test is the real check.

## 3. The cases

Nine cases, and one comparison. Each gives its `<MESSAGE>`, what you type next, and what should happen. Spread them over the five sets as you like, with the notes below. Run each in its own fresh window (section 1).

**Case 1, nothing but the clips.** `<MESSAGE>`: she wrote nothing. Expected: the first reply is the brief and nothing else: four numbered questions, each with its default, in one message, and then it waits. It has not yet touched a clip. Turn 2: type `<ANSWERS>`. Expected: one start line with a time estimate, quiet, then the reel.

**Case 2, "make a reel".** `<MESSAGE>`: `make a reel`. Expected: the same as case 1. Turn 2: `<ANSWERS>`. After the reel, in the same window, do the follow-up chain (case 8). Keep this set and its reel for case 4.

**Case 3, "20 seconds, calm, tall".** `<MESSAGE>`: `20 seconds, calm, tall`. Expected: only the two questions the message did not answer (what the reel is about, which moment is the star), numbered from 1 and 2, in one message, then it waits. It must not ask about the style, the shape or the length. Turn 2: `<ANSWERS>`, such as `1 a day at the beach, 2 the big wave`.

**Case 4, "just make it".** On case 2's set, into `work/<SET>-b/`. `<MESSAGE>`: `just make it`. Expected: no question at all, and a reel. With case 2's first reel this is the guide's brief test: the briefed reel should be clearly better (section 6).

**Case 5, "wide, for long-form video".** On the sideways talking-head set. `<MESSAGE>`: `wide, for long-form video`. Expected: no question about the shape or the length; the plan is shown first (the handbook's rule for a talking-head video) and it waits for your go; type `go ahead`; the video is wide throughout. The brief may still ask what it is about and the star moment: if so, answer with `<ANSWERS>`.

**Case 6, a file too big for the phone.** Any set. First make a file over the attachment limit, with no real video in it:

```sh
mkfile -n 401m <SCRATCH>/big.mov
```

`<MESSAGE>`: `just make it`. Add to the prompt: "and also `<SCRATCH>/big.mov`, attached last". Expected: normalize leaves that one file out with its own sentence; the reply quotes that sentence and adds one sentence on what to do next (the computer, with the file included); the reel is made from the rest.

**Case 7, a star moment the set does not hold.** Any set. `<MESSAGE>`: `make a reel`. At the brief, in turn 2, answer with a star moment that is not in the clips, for example `1 <what it is about>, 2 <a moment that is not there>, 3 lively, 4 fine`. Expected: it looks, and after looking it asks at most one more question, about that moment only, then makes the reel. A set may hold something close to the moment you name: you judge.

**Case 8, the follow-up chain.** After case 2's reel, in the same window, type these three one at a time, waiting for each reel:

1. `shorter`
2. `mute it`
3. `a wide version`

Expected, each time: a reel and a reply that names the newest numbered list; no new questions. The first reply's three follow-ups should fit that reel (see section 4). The wide version converts the clips again with the other shape and does not clone anything again. If "shorter" made `revise` drop a whole shot, the one dropped must be the last one named in that call's `--from` (the handbook says trim first, drop last).

**Case 9, the work folder gone.** After case 8, in an ordinary terminal (not the rehearsal window):

```sh
mv work/<SET> <SCRATCH>/
```

Then in the rehearsal window type `shorter`. Expected: the reply says the clips need attaching again, in the same order, and may offer the last cut list as text. It does not start over by itself. Afterwards, in the ordinary terminal, move the folder back:

```sh
mv <SCRATCH>/<SET> work/
```

**The comparison (the guide's brief test).** Cases 2 and 4 on the same set: one reel after the brief, one after "just make it". You watch both in section 6.

## 4. What to watch in every reply

- The brief comes first and alone: numbered, each question with its default, nothing about sound or music, and nothing the message or the profile already answered. "Just make it" gets no question.
- After the brief is answered, the start line is one line with a time estimate (minutes, the number of clips plus three). Then the session says nothing in its own words until the reel.
- A reply with a reel is at most two lines on what is in it, never a clip letter or a shot number, no song named, then the cover still and three follow-ups that fit the reel: "keep the sound" only if the reel was muted, "mute it" only if sound is kept, "a wide version" only for a tall reel (and the tall one for a wide reel), "move the frame" only if check noted a crop that keeps little.
- An error is the tool's own sentence plus one sentence on what to do next.

## 5. After each run

Do this in an ordinary terminal, not in the rehearsing window. Check every list, not only the first:

1. `uv run python -m v2r check --work work/<SET>` must finish with exit code 0. (With no list named, check reads `cutlist.json`.)
2. For every numbered list `cutlist-2.json`, `cutlist-3.json` and so on, in the folder: `uv run python -m v2r check work/<SET>/cutlist-<N>.json --work work/<SET>` must finish with exit code 0. (Case 9 expects nothing here: its folder was moved away.)
3. For each pair, the list and the next one, compare them with the keys sorted:

```sh
uv run python -m json.tool --sort-keys work/<SET>/cutlist.json > <SCRATCH>/a.txt
uv run python -m json.tool --sort-keys work/<SET>/cutlist-2.json > <SCRATCH>/b.txt
diff <SCRATCH>/a.txt <SCRATCH>/b.txt
```

   Do the same for `cutlist-2.json` against `cutlist-3.json`, and `cutlist-3.json` against `cutlist-4.json`. Sorting the keys means the order of fields never shows up as a difference; the order of the shots is compared as it is. Expected, for case 8:
   - after "shorter" (list 1 against list 2): only `"to"` lines, and the cover's lines if its moment was trimmed away. No `"from"` line, no `"clip"` line, no focus line, no touch-up line. If a whole shot was dropped, expect the shots after it to move up, and judge by the shot dropped being the last one the call named.
   - after "mute it" (list 2 against list 3): only `"sound"` lines.
   - after "a wide version" (list 3 against list 4): only `"width"` and `"height"` lines.
4. Note the reels' paths, `work/<SET>/reel-...mp4`, one for each stage of the chain.
5. Copy the three lists the rehearsal gave you, and these check and diff results, into this set's entry in `fixtures/reel-log.md` (private, never in the repo).

These commands were run before this kit was handed over, on a made-up work folder outside the repo: a `revise sound off` wrote the next list and exited 0, check exited 0 on both lists, and the sorted-keys diff showed only a `"sound"` line.

## 6. Watching, and the brief test

1. Watch the reels on a phone (AirDrop them), with her if possible, sound on.
2. The chain: after "shorter" the reel opens on the very same picture as before (0:00) and every shot is the same moment, only shorter; after "mute it", silence from 0:00 to the end and the same length; after "a wide version", 1920 by 1080, the sideways clips whole, the upright ones cropped onto the subject, colours as even as the tall version's, the same length and still silent.
3. The brief test: watch case 2's first reel and case 4's reel (same set), both from the same footage. The briefed one should be clearly better. If it is not, the questions are the wrong ones: change them (a handbook sentence in your own words) and try again.

## 7. Trace a bad reel

For a reel that is wrong, open a fresh window (after `/clear`) and paste:

> The reel in `work/<SET>/` is wrong at `<TIME>`: `<WHAT I SEE>`. Using its cut list, look.json and the contact sheets, tell me which of the three failed: the stills and measurements didn't show it, the handbook's words led the editor astray, or the code did something the cut list did not say. Show your evidence. Don't change anything.

A code failure stops the stage so a fix plan can be opened; a handbook failure is a sentence in your own words.

## 8. Scoring and rounds

1. In `fixtures/reel-log.md`, per case, write what happened against section 3's expectations and section 4's watch list, and for any wrong one, which of the three failed (section 7).
2. Change one thing at a time. A handbook sentence is your own text, pasted on your word with `uv run pytest tests/test_editor_handbook.py -q` passing. Then rerun only the cases it touches as the next round.
3. Stop when every case behaves as the handbook says and the briefed reel clearly beats "just make it".

## 9. What never leaves this Mac

Set names, profile text, cut lists, her words and her answers stay in `fixtures/` and `work/`, which git ignores. Nothing from a rehearsal goes into `.planning/`, `docs/` or a commit. Anything written down for the project says "set 1" to "set 5" in name order, and "profile 1", "profile 2", "profile 3", and refers to cases by number.
