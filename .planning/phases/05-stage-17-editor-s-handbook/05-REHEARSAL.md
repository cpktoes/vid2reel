# Stage 17 rehearsal kit

This is the kit for rehearsing the handbook on this Mac. It holds blanks only. It never names a fixture set, an account or a person. Fill the blanks in your own terminal or in the new Claude Code window, and keep what you fill in out of the repo.

The blanks:

- `<SET>`: the name of one folder inside `fixtures/` (one of the five sets)
- `<PROFILE>`: one account's whole "Reel style" profile, pasted in as text
- `<MESSAGE>`: what the user would type on the phone (see "The message")
- `<SCRATCH>`: a folder outside the repo, for example one made with `mktemp -d`
- `<N>`: a round number (1, 2, 3 ...)
- `<TIME>` and `<WHAT I SEE>`: where a reel looks wrong and what is wrong (only in "Trace a bad reel")

## 1. Before each rehearsal

1. Open a new Claude Code window in the repo, on the branch `stage-17-handbook`. Type `/clear`. Never use the window that is running the GSD phase: a rehearsal only means something if the session knows nothing but what the phone's Claude would know.
2. Rehearse into `work/<SET>/`, one folder per set, so the five reels sit side by side. If a folder already holds an old reel, delete the old reels in it by hand first. Render never overwrites a reel, so an old one would sit beside the new one and confuse the check.
3. Before a remake (a second round on the same set), copy the last round's cut list somewhere safe: `work/<SET>/cutlist.json` to `fixtures/rehearsals/round-<N>/<SET>.json`. Make the folder first. `fixtures/` is ignored by git, so nothing there is ever uploaded.

## 2. The rehearsal prompt

Paste this into the new window, with the blanks filled in:

> Act as the Claude in a phone chat that has just been handed EDITOR.md and knows nothing else about this project. The chat's standing instructions are this taste profile: `<PROFILE>`. The user attached the files in `fixtures/<SET>/`, in the order `ls fixtures/<SET>` lists them, and wrote: "`<MESSAGE>`". Follow EDITOR.md exactly, step by step, using only the repo's commands. Put everything in `work/<SET>/`.
>
> Mac adaptations (these are adaptations, never gaps in the handbook):
> - Run every v2r command as `uv run python -m v2r ...` from the top of the repo, instead of `python3 -m v2r ...`. The Mac's own Python is too old and lacks packages the phone has.
> - Add `--work work/<SET>` to `normalize` (before its `--`), `look`, `check`, `match` and `render`.
> - Read every `work/` in EDITOR.md as `work/<SET>/`. The cut list is `work/<SET>/cutlist.json`.
> - Never run `normalize` without `--work work/<SET>`: a plain run clears the folder of the last job.
>
> Reads: read only EDITOR.md, `schema/cutlist.schema.json`, the attached files, the contact sheets, `look.json`, `manifest.json`, the proof sheets and the commands' own output and logs. Do not open anything under `.planning/`, `docs/` or `v2r/`. Do not open `CLAUDE.md`, the taste notes, any other profile or the reel log. Set aside anything you already know about this project from memory or from project instructions. If you are tempted to open or use any of those, do not, and say so at the end.
>
> When you have finished, show me the cut list and tell me where the reel and its cover are, as you would reply on the phone. Then, stepping out of the role, give three lists: every place where EDITOR.md was unclear or where you were tempted to do something it didn't say; the Mac adaptations you used; any file you read beyond the ones allowed.

Two honest limits. Claude Code still loads the repo's `CLAUDE.md` and its memory by itself, so the prompt can only ask the session to set them aside. The third list is the check: if it names a file the phone could not have, the run proves less. And the rehearsal proves the handbook's flow, not the phone's sandbox.

## 3. The message

`<MESSAGE>` is `make a reel, about 20 seconds.` for every set except the sideways talking-head set. That set is always made wide, so its message is `make a wide video for YouTube, about <N> seconds.` and you choose the length.

## 4. One unreadable file

On one set only, test the "carry on and say which" rule. First make a file that is not a video:

```sh
printf 'not a video' > <SCRATCH>/broken.mov
```

Then add to the prompt: "and also `<SCRATCH>/broken.mov`, attached last". What should happen: `normalize` prints one sentence about that file, the reel is still made from the rest, and the reply names the file.

## 5. After each run

Do this in an ordinary terminal, not in the rehearsing window:

1. `uv run python -m v2r check --work work/<SET>` must finish with exit code 0.
2. Note the reel's path, `work/<SET>/reel-...mp4`.
3. Copy the three lists the rehearsal gave you into this set's entry in `fixtures/reel-log.md` (private, never in the repo).

## 6. The second profile

For the profile test, use the same set with a different account's profile, into a new folder `work/<SET>-b`. The attached files stay `fixtures/<SET>/`. Change only the profile in the prompt and the `--work` folder, everything else word for word.

Optional control, to see how much two runs of the same thing differ by chance: run the first profile again into `work/<SET>-c`. Whatever differs between `work/<SET>` and `work/<SET>-c` is noise, and cannot be blamed on a profile.

## 7. Comparing the two cut lists

```sh
uv run python -m json.tool --sort-keys work/<SET>/cutlist.json > <SCRATCH>/a.txt
uv run python -m json.tool --sort-keys work/<SET>-b/cutlist.json > <SCRATCH>/b.txt
diff <SCRATCH>/a.txt <SCRATCH>/b.txt
```

Sorting the keys means the order of fields never shows up as a difference. The order of the segments is compared as it is, because the order of the shots is the edit.

Judge by category, not line by line:

- length: the number of shots and the total seconds
- recipe: the shot lengths
- the opening and closing shots: which clip, which second
- sound: kept or off
- moves
- filter
- canvas

Ignore the wording of the "why" notes and tiny decimals in the focus points.

The two cut lists "differ only where the profiles differ" when every category that differs is one the two profiles disagree on, and every other category is the same, or differs no more than the control run does. If everything is the same, the profile was probably not read. If everything is different, the handbook is too loose.

The Mac has FFmpeg 8 and no 30 MiB limit on what comes back, so only the phone test proves the sandbox.

## 8. Trace a bad reel

For a reel that is wrong, open a fresh window (after `/clear`) and paste:

> The reel in `work/<SET>/` is wrong at `<TIME>`: `<WHAT I SEE>`. Using its cut list, look.json and the contact sheets, tell me which of the three failed: the stills and measurements didn't show it, the choice in the cut list was poor, or the video doesn't match the cut list. Show your evidence. Don't change anything.

## 9. Scoring

1. Watch all five reels on a phone, with her if possible.
2. In `fixtures/reel-log.md`, per reel, write: the score from 1 to 5, what was wrong in her words, the profile used, and, for the worst one, which of the three things failed (section 8).
3. Change one thing, remake all five, compare. Stop when she would post at least three of the five with small changes.
4. A change to EDITOR.md is the user's own text: he edits it, or asks for a pasted change.

## 10. What never leaves this Mac

Set names, profile text, cut lists, her words and her scores stay in `fixtures/` and `work/`, which git ignores. Nothing from a rehearsal goes into `.planning/`, `docs/` or a commit. Anything written down for the project says "set 1" to "set 5" in name order, and "profile 1", "profile 2", "profile 3".
