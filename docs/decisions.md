# Decisions

One dated line per decision: the stage, what was decided, and how it differs from the guide (docs/field-guide.html). Where this file disagrees with the guide, this file wins. Never name a person or an account here.

- 2026-10-11 · Stage 16 · A wide clip in a tall reel is cropped to fill the frame, centred on the subject; never bars, never mixed with widescreen. Same as the guide.
- 2026-10-11 · Stage 19 · The chat asks a brief of three to five quick questions before editing. Same as the guide.
- 2026-10-12 · Stage 10 · The toolbox reaches the phone through this public repo, fetched each time by a small skill. Same as the guide.
- 2026-10-12 · Stage 23 · Long videos are finished on a Mac from start to finish. Same as the guide's Stage 23, but its Stage 12 still says only three Decide boxes are settled.
- 2026-10-12 · Stage 09 · Python 3.13 is the minimum, matching the sandbox's Python 3.13.16. The guide names no version.
- 2026-10-12 · Stage 11 · SKILL.md installs requirements with `pip install --break-system-packages`, which Linux sandboxes often require. Not in the guide's prompt.
- 2026-10-12 · Stage 11 · The fit update caps the bitrate on the normal quality setting, and steps the frame down from full size to 2/3 and then 1/2 below 2.5, 1.2 and 0.7 Mbit/s (`FIT_STEPS` in settings.py). The guide gives the goal, not these numbers.
- 2026-10-12 · Stage 11 · EDITOR.md starts the join in the background and reads join.log until it finishes, because the sandbox stops any single command after 2 minutes. The guide's five lines don't cover this.
- 2026-10-12 · Stage 11 · EDITOR.md says one clip is fine to join, after the chat's Claude refused a one-clip join. The guide says only "join them".
- 2026-10-12 · Stage 11 · `MAX_ATTACHMENT_BYTES` is 400 MB, the app's warning point, with no margin below it, because a 408.7 MB file arrived. `MAX_ATTACHMENTS` is 10, the most files tried. The guide asked for limits with a safety margin.
- 2026-10-12 · Stage 13 · The guide's sixteenth edition was made from Claude Code at my request: the published guide was edited directly and docs/field-guide.html replaced with the result. The guide's routine has the planning chat make revisions.
- 2026-10-12 · Stage 11 · The phone tests differed from the guide's table. Test 3 ran first with a 1-minute 1080p clip, then with a 30-second 4K clip. Test 4 used a 3-minute clip instead of 60 to 90 seconds. An extra test checked a 408 MB upload. Details are in docs/phone-limits.md.
