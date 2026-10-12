---
name: vid2reel
description: Makes reels from the user's own clips with Vid2Reel's code. Use this skill whenever someone attaches video clips or photos and asks for a reel, a short video, an edit or a montage.
---

1. Make a shallow clone of the main branch of the public repo https://github.com/cpktoes/vid2reel.git into a temporary folder, or of another branch if the user's message names one (for example "use branch stage-15-look" means `--branch stage-15-look`):
   `D=$(mktemp -d) && git clone --depth 1 --branch main https://github.com/cpktoes/vid2reel.git "$D" && echo "$D"`
   Run every later command from that folder.
2. If the clone fails, say "I can't reach Vid2Reel's code right now", show the error, and stop. Do not improvise an edit.
3. Install the libraries: `python3 -m pip install --break-system-packages -r requirements.txt`
4. Read EDITOR.md in full and follow it exactly. Use only the commands in the repo; never write your own FFmpeg commands.
