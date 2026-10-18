"""Entry point for `python3 -m v2r` and the `v2r` command."""

import argparse
import subprocess
import sys
from pathlib import Path

from v2r import __version__, build_skill, doctor, join, look, normalize, settings


def main(argv=None):
    # allow_abbrev=False everywhere: a file name such as "--sh=wide" must never be read as a shortened option.
    # Put "--" before file names (python3 -m v2r normalize --shape tall -- FILE ...) and argparse treats all that follows as files.
    parser = argparse.ArgumentParser(prog="v2r", description="Command-line video toolbox.", allow_abbrev=False)
    parser.add_argument("--version", action="version", version=f"v2r {__version__}")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("doctor", help="report on the computer v2r is running on", allow_abbrev=False)
    join_parser = commands.add_parser("join", help="join videos into one MP4 in work/", allow_abbrev=False)
    join_parser.add_argument(
        "--shape",
        required=True,
        choices=list(settings.SHAPES),
        help=" or ".join(f"{name} ({w}x{h})" for name, (w, h) in settings.SHAPES.items()) + "; there is no default",
    )
    join_parser.add_argument("videos", nargs="+", type=Path, help="video files, in the order to join them")
    normalize_parser = commands.add_parser(
        "normalize", help="convert clips to one working format in work/", allow_abbrev=False)
    normalize_parser.add_argument(
        "--shape",
        required=True,
        choices=list(settings.SHAPES),
        help=" or ".join(f"{name} ({w}x{h})" for name, (w, h) in settings.SHAPES.items()) + "; there is no default",
    )
    normalize_parser.add_argument(
        "files", nargs="+", type=Path,
        help="files, in the order they were attached; they get the letters A, B, C...",
    )
    look_parser = commands.add_parser(
        "look", help="make contact sheets and measurements of the working copies in work/", allow_abbrev=False)
    look_parser.add_argument(
        "work", nargs="?", type=Path, default=None,
        help="the work folder that holds manifest.json; leave out for work/ in this repo",
    )
    commands.add_parser("build-skill", help="build skill/vid2reel.zip for uploading to Claude", allow_abbrev=False)
    args = parser.parse_args(argv)

    if args.command == "doctor":
        doctor.run()
    elif args.command == "join":
        try:
            output, summary = join.join(args.videos, args.shape)
        except join.JoinError as error:
            print(f"v2r join: {error}", file=sys.stderr)
            return 1
        except subprocess.CalledProcessError:
            print("v2r join: FFmpeg failed; its error is shown above.", file=sys.stderr)
            return 1
        print(summary)
        print(output)
    elif args.command == "normalize":
        try:
            manifest = normalize.normalize(args.files, args.shape)
        except normalize.NormalizeError as error:
            print(f"v2r normalize: {error}", file=sys.stderr)
            return 1
        return 0 if any(clip["status"] == "done" for clip in manifest["clips"]) else 1
    elif args.command == "look":
        try:
            result = look.look(args.work)
        except look.LookError as error:
            print(f"v2r look: {error}", file=sys.stderr)
            return 1
        return 0 if any(clip["status"] == "done" for clip in result["clips"]) else 1
    elif args.command == "build-skill":
        print(build_skill.build())
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
