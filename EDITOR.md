1. From the top of this repo, run `python3 -m v2r doctor`.
2. Find the video files the user attached to the chat.
3. Join them in the order they were attached. The sandbox stops any command after 2 minutes, so start the join in the background: `nohup sh -c 'python3 -m v2r join --shape tall FILE1 FILE2 ...; echo "join finished with exit code $?"' > join.log 2>&1 &`, using `--shape wide` instead only if the user asks for wide. Then read `join.log` every 30 seconds until it says "join finished", and use what it printed.
4. Send the file whose path the join command prints back to the user as a file.
5. If anything fails, show the user the exact error and stop.
