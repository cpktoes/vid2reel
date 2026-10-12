# Phone limits

Measured on 2026-10-12 by using the vid2reel skill from the Claude app on a phone, which runs v2r in Claude's cloud workspace (the sandbox). "Not recorded" means the tests didn't capture that number; nothing here is estimated unless it says so.

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
| Largest file that arrived | Size not recorded. The longest clip that arrived was a 3-minute 1080p clip. |
| Smallest file that failed | None failed. The app shows an upload warning for files over 400 MB; whether such a file then arrives, and the warning's text, were not recorded. |
| Arrived at phone size or smaller | Not recorded. |
| Most files in one message | 10 short clips (about 15 s or less each); all arrived. A message with 3 photos and 1 clip also arrived. |

## How long each step took

| Step | Test | Time |
| --- | --- | --- |
| `doctor` | 3-minute clip | about 1 s |
| `join --shape tall` | one 3-minute 1080p clip | about 467 s (7.8 min) |

The clone, the pip install, the uploads and the other tests' joins were not timed. No time limit was hit, but none was looked for: 467 s is simply the longest step seen.

## What came back

| Measure | Result |
| --- | --- |
| Largest tall result sent back | None. Every result whose delivery was recorded was refused for being over the 30 MiB send limit (below). |
| Largest wide result sent back | None; no wide test was run. |
| Longest wide video that came back | None; no wide test was run. |

Results that were built but refused:

| Test | Shape | Result size |
| --- | --- | --- |
| one 1-minute 1080p clip | not recorded (EDITOR.md's default is tall) | 44.8 MiB |
| 10 short clips | not recorded (EDITOR.md's default is tall) | 58.7 MiB |
| one 3-minute 1080p clip | tall | 95.9 MiB (100,539,471 bytes, `join-tall-20261012-143223.mp4`) |

With 3 photos and 1 clip, Claude reported: "Only the .mov is a video, so the join used just that clip. The three photos were not included in the reel." Whether that reel was sent back was not recorded.

## Errors, exact text

1. One 1-minute clip: "The reel is built, but I couldn’t send it to you. The file is 44.8 MiB and the upload limit is 30 MiB. Vid2Reel has no option to make a smaller export, and I’m not allowed to write my own FFmpeg commands, so I’ve stopped here."
2. One 3-minute clip: "Delivery failed: the send was refused with this message: “95.9 MiB exceeds the 30 MiB upload limit — send a smaller or compressed copy.”"
3. Ten short clips: "The reel is built, but I couldn’t send it. The file is 58.7 MiB and the upload limit is 30 MiB. Per your instructions I’m stopping here."
4. Files over 400 MB: an upload warning appeared; its text was not recorded.

Errors 1 and 3 are Claude's wording. Only error 2 quotes the sandbox's own refusal.

## What the numbers mean (estimates)

- A result comes back only if it is at most 30 MiB. At today's join settings the results ran 32 to 45 MiB per minute of video, so only reels shorter than about 40 seconds would fit, or about 32 seconds within the safety margin below.
- The sandbox's join took about 2.6 seconds per second of video (the 3-minute tall clip, 2 processors). The Mac takes about 1.3 (8 processors).

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
| `MAX_ATTACHMENTS` | 10 | the most files tried, all of which arrived; no margin, because 10 is a tested success, not a limit that was found |
| `MAX_RESULT_BYTES` | 24 MiB | 80% of the 30 MiB send limit |
