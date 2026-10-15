# Phone limits

Measured on 2026-10-12 by running the seven tests of the guide's Stage 11 from the Claude app on a phone. The app runs v2r in Claude's cloud workspace (the sandbox). Test 7 ran after the fit update, which keeps every result under `MAX_RESULT_BYTES`. "Not recorded" means the tests didn't capture that number; nothing here is estimated unless it says so.

## The tests

| Test | Attached | Outcome |
| --- | --- | --- |
| 1 | Two clips of about 10 s | The reel came back and played fine. |
| 2 | One clip of about 30 s | The reel came back and played fine. |
| 3a | One 1-minute 1080p clip, run first in place of the guide's 30-second 4K clip | It arrived and the reel was built (44.8 MiB), but sending it back was refused: over 30 MiB. |
| 3b | One 30-second 4K landscape clip (103.3 MB on the phone); a 7.5-second landscape HDR clip (1920×1080 as shown, stored as 1080×1920 with a 90° rotation flag) added for the second attempt. Joined wide. | Attempt 1, the 4K clip alone: it arrived, but Claude wouldn't "join" a single file, though the command accepts one. Attempt 2, with the second clip: the join ran in the background and took 142.96 s. The result came back at 1920×1080, 19.4 MiB, and looked fine. |
| 3c | One 4K HDR clip of 2 min 7 s, 408 MB on the phone. No reel; only checked whether it arrived. | It arrived whole: 408,714,877 bytes, 3840×2160, 30 fps, 126.9 s, still HEVC 10-bit HLG HDR. |
| 4 | One 3-minute 1080p clip, in place of the guide's 60 to 90 seconds | It arrived and the reel was built (95.9 MiB) in about 467 s, but sending it back was refused: over 30 MiB. |
| 5 | Ten short clips of about 15 s or less | All ten arrived and the reel was built (58.7 MiB), but sending it back was refused: over 30 MiB. |
| 6 | Three photos and one short clip | All four arrived. The reel was made from the clip alone. Whether it came back was not recorded. |
| 7 | One sideways clip of someone talking: 1920×1080 HDR (HLG), about 3 min 25 s, 236.6 MB on the phone. Joined wide. | Attempts 1 and 2 were stopped by the sandbox's 2-minute command limit. Attempt 3 ran the join in the background and finished in 142 s. The result came back: 960×540, 17.2 MiB. It looked great on a computer screen and on the phone. |
| 8 | Stage 14 (2026-10-14): six HDR (HLG + Dolby Vision) clips of 14 to 86 MB plus the 408.7 MB clip from test 3c; normalize, then join tall. | All six were tried. The 408.7 MB clip was left out by `MAX_ATTACHMENT_BYTES` with one plain sentence. The first join was refused: 4 min 9 s is over the 3 min 54 s the smallest step can hold. With the longest clip left out, 2 min 10 s came back at 720×1280, 20.6 MB, and looked right. |
| 9 | Stage 14: two HDR clips (about 42 s and 8 s) and five pictures picked from the camera roll (two camera photos, three screenshots); a fresh copy of the branch. Tall. | All seven converted. The pictures arrived as JPEG and PNG named `image.jpg` and `image.png`, not HEIC. Each became a 4-second still. The reel came back at 1080×1920, 17.5 MB, about 70 s, and looked right. |
| 10 | Stage 14: test 9's files plus two HEIC photos of 5712×3213 attached from the Files app. Tall. | All nine converted; the HEICs kept their names and format and became stills. The reel, about 78 s, came back at 720×1280, 15.5 MB, and looked right. The size step is explained below. |

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
| Largest file that arrived | 408,714,877 bytes (test 3c), 408 MB on the phone |
| Smallest file that failed | None failed. The app warns about files over 400 MB, but test 3c's 408.7 MB file arrived anyway. The warning's text was not recorded. |
| Arrived at phone size or smaller | At phone size, unchanged. Test 3c's clip was 408 MB on the phone and arrived at 408,714,877 bytes, still 4K HEVC HDR. Test 3b's 7.5-second clip arrived at 8,725,576 bytes, byte for byte the size of the original sent to the Mac by AirDrop. Uploads arrive as the original file, not a shrunk copy. |
| Most files in one message | 10 (test 5), and all arrived. |
| Where attachments land | `/mnt/user-data/uploads/` in the sandbox (test 7) |
| Pictures picked from the camera roll | Arrive as JPEG (camera photos) or PNG (screenshots) named `image.jpg` or `image.png`; the HEIC original is not preserved (test 9). |
| Pictures attached from the Files app | Arrive as the original HEIC with their own name (test 10, two of 5712×3213). |

## How long each step took

| Step | Test | Time |
| --- | --- | --- |
| `doctor` | 4 | about 1 s |
| `join --shape tall` | 4 (3 minutes, full size 1080×1920) | about 467 s (7.8 min) |
| `join --shape wide` | 7 (3 min 25 s, fitted to 960×540) | 142.27 s |
| `join --shape wide` | 3b (30 s of 4K plus 7.5 s of 1080p, full size 1920×1080) | 142.96 s |
| `normalize --shape tall` | 8, 9, 10 (1080p HDR clips) | about 2 seconds of work per second of video: a 42 s clip took 80 s, an 8 s clip 24 s, a 47 s clip 103.5 s (lengths estimated from the reel totals). A picture takes 1 to 3 s. |

The clone, the pip install, the uploads and the other tests' joins were not timed.

**The sandbox stops any single command after 2 minutes** (test 7). It reports exit code 143 and "Command timed out after 2m 0s." A join started in the background with `nohup ... &`, whose log is then read until it finishes, is not stopped (test 7, attempt 3). EDITOR.md now starts every join that way. How test 4's 467-second join finished in a single command was not recorded.

## What came back

| Measure | Result |
| --- | --- |
| Largest tall result sent back | Test 2's reel, from a clip of about 30 s. Its size was not recorded. The smallest result refused was 44.8 MiB (test 3). |
| Largest wide result sent back | 19.4 MiB (test 3b) |
| Longest wide video that came back | 205.44 s, about 3 min 25 s (test 7) |
| Longest tall video that came back | 2 min 10 s at 720×1280, 20.6 MB (test 8) |
| Longest tall video at full size | about 70 s at 1080×1920, 17.5 MB (test 9); 78 s stepped down to 720×1280 (test 10) |

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
4. Files over 400 MB: an upload warning appeared; its text was not recorded. Test 3c's file arrived despite it.
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
- Uploads arrive as the original file, at full size and quality (test 3c). At 4K that is about 3.2 MB per second of video, so 400 MB is about 2 minutes of 4K. Test 7's 1080p clip came to about 1.15 MB per second, so 400 MB is about 6 minutes of 1080p.
- Claude's own description of a clip can get its shape wrong. It reported test 3b's second clip as "1080 × 1920 (portrait)", reading the stored size and ignoring the rotation flag. v2r's join applied the flag and showed the clip whole in the wide video.
- 4K is the slowest to read. Test 3b took about 3.8 seconds of work per second of video (30 s of 4K plus 7.5 s of 1080p, at full size). So even a 30-second 4K clip runs past the 2-minute limit and needs the background join.

- Converting is quicker than joining: normalize needs about 2 seconds of work per second of 1080p HDR video (tests 8 to 10), against 2.6 for a full-size join. `FFMPEG_SECONDS_PER_SECOND` = 10 therefore leaves a margin of four to five times, even allowing for 4K being slower.
- The join picks the frame size from the reel's length alone, before encoding: 1080×1920 up to about 73 s, 720×1280 to about 2 min 26 s, 540×960 to 3 min 54 s, refused beyond that. Tests 9 and 10 sit either side of the first line: 70 s came back at full size, 78 s at 720×1280. Still pictures need far fewer bits than the join assumes, so a reel with stills can come back well under the limit at a smaller size than it needed; encoding first and measuring belongs to the stage that builds the final video.

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
| `MAX_ATTACHMENT_BYTES` | 400 MB | the size above which the app warns. A 408.7 MB file still arrived (test 3c), so this line sits just below a tested success. The real ceiling was not found. |
| `MAX_ATTACHMENTS` | 10 | test 5: the most files tried, all of which arrived; no margin, because 10 is a tested success, not a limit that was found |
| `MAX_RESULT_BYTES` | 24 MiB | 80% of the 30 MiB send limit |
| `FFPROBE_TIMEOUT` | 30 s | a hang guard for reading one file's facts; reading does not decode, so a few seconds is normal |
| `FFMPEG_TIMEOUT_FLOOR` | 120 s | a hang guard: start-up plus a picture's 4-second still, added to every conversion's allowance |
| `FFMPEG_SECONDS_PER_SECOND` | 10 | a hang guard, not a speed goal: tests 8 to 10 measured about 2 for 1080p HDR and test 3b 3.8 for a 4K join |
| `MAX_PHOTO_PIXELS` | 80 million | not a measured limit: a 48 MP iPhone photo is 48 million and a panorama about 63 million, so this refuses only absurd files |
| `MAX_VIDEO_SIDE` | 8192 pixels | not a measured limit: an iPhone's 4K frame is 3840 wide, so this refuses only absurd files |

The 2-minute command limit is not a setting. EDITOR.md handles it by starting the join in the background.
