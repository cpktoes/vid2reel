# Phone limits

Measured on 2026-10-12 by running the seven tests of the guide's Stage 11 from the Claude app on a phone. The app runs v2r in Claude's cloud workspace (the sandbox). "Not recorded" means the tests didn't capture that number; nothing here is estimated unless it says so.

## The tests

| Test | Attached | Outcome |
| --- | --- | --- |
| 1 | Two clips of about 10 s | The reel came back and played fine. |
| 2 | One clip of about 30 s | The reel came back and played fine. |
| 3 | One 1-minute 1080p clip, in place of the guide's 30-second 4K clip | It arrived and the reel was built (44.8 MiB), but sending it back was refused: over 30 MiB. |
| 4 | One 3-minute 1080p clip, in place of the guide's 60 to 90 seconds | It arrived and the reel was built (95.9 MiB) in about 467 s, but sending it back was refused: over 30 MiB. |
| 5 | Ten short clips of about 15 s or less | All ten arrived and the reel was built (58.7 MiB), but sending it back was refused: over 30 MiB. |
| 6 | Three photos and one short clip | All four arrived. The reel was made from the clip alone. Whether it came back was not recorded. |
| 7 | Test 4's clip joined with itself three times, wide | Not run: results over 30 MiB were already being refused. |

## The sandbox's doctor report

```
v2r doctor: a report on this computer

FFmpeg 6.1.1-3ubuntu5 is installed.
ffprobe 6.1.1-3ubuntu5 is installed.
The H.264 video encoder (libx264) is available.
The AAC audio encoder (aac) is available.
The scale filter is available.
The crop filter is available.
The zscale filter is available.
The tonemap filter is available.
The loudnorm filter is available.
The drawtext filter is available.
Python is version 3.13.16.
This computer has 2 processors.
32.2 GB of disk space is free.
7.9 GB of memory is free.
github.com can be reached.
pypi.org can be reached.
```

## What arrived

| Measure | Result |
| --- | --- |
| Largest file that arrived | The 3-minute 1080p clip of test 4; its size was not recorded. |
| Smallest file that failed | None failed. The app showed an upload warning for files over 400 MB. Which file triggered it, whether such a file then arrives, and the warning's text were not recorded. |
| Arrived at phone size or smaller | Not recorded. |
| Most files in one message | 10 (test 5), and all arrived. |

## How long each step took

| Step | Test | Time |
| --- | --- | --- |
| `doctor` | 4 | about 1 s |
| `join --shape tall` | 4 (one 3-minute 1080p clip) | about 467 s (7.8 min) |

The clone, the pip install, the uploads and the other tests' joins were not timed. No time limit was hit, but none was looked for: 467 s is simply the longest step seen.

## What came back

| Measure | Result |
| --- | --- |
| Largest tall result sent back | Test 2's reel, from a clip of about 30 s. Its size was not recorded. The smallest result refused was 44.8 MiB (test 3). |
| Largest wide result sent back | None; test 7 (wide) wasn't run. |
| Longest wide video that came back | None; test 7 wasn't run. |

Results that were built but refused:

| Test | Shape | Result size |
| --- | --- | --- |
| 3 | not recorded (EDITOR.md's default is tall) | 44.8 MiB |
| 5 | not recorded (EDITOR.md's default is tall) | 58.7 MiB |
| 4 | tall | 95.9 MiB (100,539,471 bytes, `join-tall-20261012-143223.mp4`) |

Sending to the Mac has the same cap. Claude reported: "both ways of getting a file to you are capped at 30 MiB per file: the chat download and the transfer to your Mac. The Mac is linked, but no folder on it is connected yet, so I’d need you to approve access to one before anything could be sent." This is Claude's report; the transfer itself wasn't tried.

## Errors, exact text

1. Test 3: "The reel is built, but I couldn’t send it to you. The file is 44.8 MiB and the upload limit is 30 MiB. Vid2Reel has no option to make a smaller export, and I’m not allowed to write my own FFmpeg commands, so I’ve stopped here."
2. Test 4: "Delivery failed: the send was refused with this message: “95.9 MiB exceeds the 30 MiB upload limit — send a smaller or compressed copy.”"
3. Test 5: "The reel is built, but I couldn’t send it. The file is 58.7 MiB and the upload limit is 30 MiB. Per your instructions I’m stopping here."
4. Files over 400 MB: an upload warning appeared; its text was not recorded.

Errors 1 and 3 are Claude's wording. Only error 2 quotes the sandbox's own refusal.

Test 6 was not an error. Claude reported: "Only the .mov is a video, so the join used just that clip. The three photos were not included in the reel."

## What the numbers mean (estimates)

- A result comes back only if it is at most 30 MiB. Tests 1 and 2 (reels of about 20 and 30 seconds) came back. Tests 3 to 5 (a minute or more) were refused.
- At today's join settings, results ran 32 to 45 MiB per minute of video. So the cut-off is about 40 seconds, or about 32 seconds within the safety margin below.
- A wide frame has as many pixels as a tall one, so the same cut-off probably applies to wide videos. Test 7 would confirm it.
- The sandbox's join took about 2.6 seconds per second of video (test 4, 2 processors). The Mac takes about 1.3 (8 processors).

## What the sandbox's doctor report lacks that the Mac's has

Every check passes in both: the same encoders and filters are available, and both can reach github.com and pypi.org. The sandbox has less of four things:

| Item | Sandbox | Mac (2026-10-12) |
| --- | --- | --- |
| FFmpeg and ffprobe | 6.1.1 | 8.0.1, two major versions newer. Anything that works on the Mac must be checked against 6.1. |
| Processors | 2 | 8, which is why joins are slower in the sandbox |
| Free disk space | 32.2 GB | 63.0 GB |
| Free memory | 7.9 GB | 10.8 GB |

Python is 3.13.16 in the sandbox and 3.13.15 on the Mac, which makes no difference.

## Limits set in v2r/settings.py

| Setting | Value | From |
| --- | --- | --- |
| `MAX_ATTACHMENT_BYTES` | 320 MB | 80% of the 400 MB upload warning |
| `MAX_ATTACHMENTS` | 10 | test 5: the most files tried, all of which arrived; no margin, because 10 is a tested success, not a limit that was found |
| `MAX_RESULT_BYTES` | 24 MiB | 80% of the 30 MiB send limit |
