# Phone limits

Measured on 2026-10-12 by running the seven tests of the guide's Stage 11 from the Claude app on a phone. The app runs v2r in Claude's cloud workspace (the sandbox). Test 7 ran after the fit update, which keeps every result under `MAX_RESULT_BYTES`. "Not recorded" means the tests didn't capture that number; nothing here is estimated unless it says so.

## The tests

| Test | Attached | Outcome |
| --- | --- | --- |
| 1 | Two clips of about 10 s | The reel came back and played fine. |
| 2 | One clip of about 30 s | The reel came back and played fine. |
| 3a | One 1-minute 1080p clip, run first in place of the guide's 30-second 4K clip | It arrived and the reel was built (44.8 MiB), but sending it back was refused: over 30 MiB. |
| 3b | One 30-second 4K landscape clip (103.3 MB on the phone); a 7.5-second 1080×1920 HDR clip added for the second attempt. Joined wide. | Attempt 1, the 4K clip alone: it arrived, but Claude wouldn't "join" a single file, though the command accepts one. Attempt 2, with the second clip: the join ran in the background and took 142.96 s. The result came back at 1920×1080, 19.4 MiB, and looked fine. |
| 4 | One 3-minute 1080p clip, in place of the guide's 60 to 90 seconds | It arrived and the reel was built (95.9 MiB) in about 467 s, but sending it back was refused: over 30 MiB. |
| 5 | Ten short clips of about 15 s or less | All ten arrived and the reel was built (58.7 MiB), but sending it back was refused: over 30 MiB. |
| 6 | Three photos and one short clip | All four arrived. The reel was made from the clip alone. Whether it came back was not recorded. |
| 7 | One sideways clip of someone talking: 1920×1080 HDR (HLG), about 3 min 25 s, 236.6 MB on the phone. Joined wide. | Attempts 1 and 2 were stopped by the sandbox's 2-minute command limit. Attempt 3 ran the join in the background and finished in 142 s. The result came back: 960×540, 17.2 MiB. It looked great on a computer screen and on the phone. |

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
| Largest file that arrived | Test 7's clip, 236.6 MB on the phone. Its size as it arrived was not recorded. Test 3b's 4K clip (103.3 MB on the phone) also arrived; its size as it arrived was not recorded either. |
| Smallest file that failed | None failed. The app showed an upload warning for files over 400 MB. Which file triggered it, whether such a file then arrives, and the warning's text were not recorded. |
| Arrived at phone size or smaller | Not yet known. Test 3b's 1080p clip arrived at 8,725,576 bytes, but its size on the phone was not recorded. |
| Most files in one message | 10 (test 5), and all arrived. |
| Where attachments land | `/mnt/user-data/uploads/` in the sandbox (test 7) |

## How long each step took

| Step | Test | Time |
| --- | --- | --- |
| `doctor` | 4 | about 1 s |
| `join --shape tall` | 4 (3 minutes, full size 1080×1920) | about 467 s (7.8 min) |
| `join --shape wide` | 7 (3 min 25 s, fitted to 960×540) | 142.27 s |
| `join --shape wide` | 3b (30 s of 4K plus 7.5 s of 1080p, full size 1920×1080) | 142.96 s |

The clone, the pip install, the uploads and the other tests' joins were not timed.

**The sandbox stops any single command after 2 minutes** (test 7). It reports exit code 143 and "Command timed out after 2m 0s." A join started in the background with `nohup ... &`, whose log is then read until it finishes, is not stopped (test 7, attempt 3). EDITOR.md now starts every join that way. How test 4's 467-second join finished in a single command was not recorded.

## What came back

| Measure | Result |
| --- | --- |
| Largest tall result sent back | Test 2's reel, from a clip of about 30 s. Its size was not recorded. The smallest result refused was 44.8 MiB (test 3). |
| Largest wide result sent back | 19.4 MiB (test 3b) |
| Longest wide video that came back | 205.44 s, about 3 min 25 s (test 7) |

Test 7's join reported: "The video is 960x540 at an average of 0.7 Mbit/s, and the file is 17.2 MiB, under the 24 MiB limit." Test 3b's reported: "The video is 1920x1080 at an average of 4.2 Mbit/s, and the file is 19.4 MiB, under the 24 MiB limit." Claude described the result as an SDR re-encode, but the join doesn't convert HDR to SDR. The file keeps the source's HDR (HLG) label, as the same join does on the Mac, and it looked great anyway.

Results that were built but refused (all before the fit update):

| Test | Shape | Result size |
| --- | --- | --- |
| 3a | not recorded (EDITOR.md's default is tall) | 44.8 MiB |
| 5 | not recorded (EDITOR.md's default is tall) | 58.7 MiB |
| 4 | tall | 95.9 MiB (100,539,471 bytes, `join-tall-20261012-143223.mp4`) |

Sending to the Mac has the same cap. Claude reported: "both ways of getting a file to you are capped at 30 MiB per file: the chat download and the transfer to your Mac. The Mac is linked, but no folder on it is connected yet, so I’d need you to approve access to one before anything could be sent." This is Claude's report; the transfer itself wasn't tried.

## Errors, exact text

1. Test 3a: "The reel is built, but I couldn’t send it to you. The file is 44.8 MiB and the upload limit is 30 MiB. Vid2Reel has no option to make a smaller export, and I’m not allowed to write my own FFmpeg commands, so I’ve stopped here."
2. Test 4: "Delivery failed: the send was refused with this message: “95.9 MiB exceeds the 30 MiB upload limit — send a smaller or compressed copy.”"
3. Test 5: "The reel is built, but I couldn’t send it. The file is 58.7 MiB and the upload limit is 30 MiB. Per your instructions I’m stopping here."
4. Files over 400 MB: an upload warning appeared; its text was not recorded.
5. Test 7, attempt 1: a 2-minute tool timeout; its text was not recorded.
6. Test 7, attempt 2: "Exit code 143, then “Command timed out after 2m 0s.” The process was killed by SIGTERM at the tool’s time limit and printed no output."
7. Test 3b, attempt 1 (one file): "Only one file arrived, so I haven’t joined anything. The upload folder has just IMG_3178.mov. If you meant to attach a second clip, please upload it again and I’ll join the two wide, in the order you attached them. Join: not run. The join step needs at least two clips, and I didn’t want to produce a one-clip “join”."

Errors 1, 3 and 7 are Claude's wording. Errors 2 and 6 quote the sandbox's own messages. Error 7 came from EDITOR.md's wording, not from a limit: the join command accepts a single file. Step 3 now says so.

Test 6 was not an error. Claude reported: "Only the .mov is a video, so the join used just that clip. The three photos were not included in the reel."

## What the numbers mean (estimates)

- A result comes back only if it is at most 30 MiB. Before the fit update, results ran 32 to 45 MiB per minute of video, so nothing over about 40 seconds came back.
- The fit update lifts that ceiling: it lowers the bitrate, then the frame size, until the video fits. Test 7's 3 min 25 s of wide came back at 960×540 and 17.2 MiB, and looked great. The longest video the fit will make at the smallest step is 3 min 54 s, in either shape.
- Any single command is stopped after 2 minutes. At full size, the join needs about 2.6 seconds of work per second of video (test 4), so anything over about 45 seconds would be stopped. That is why the join runs in the background.
- Frame size sets the speed. At 960×540 the join needed about 0.7 seconds of work per second of video (test 7), nearly four times quicker than at full size (test 4). The Mac needs about 1.3 at full size (8 processors).
- 4K is the slowest to read. Test 3b took about 3.8 seconds of work per second of video (30 s of 4K plus 7.5 s of 1080p, at full size). So even a 30-second 4K clip runs past the 2-minute limit and needs the background join.

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

The 2-minute command limit is not a setting. EDITOR.md handles it by starting the join in the background.
