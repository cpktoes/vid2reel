"""Entry point for `python3 -m v2r` and the `v2r` command."""

import argparse
import subprocess
import sys
from pathlib import Path

from v2r import __version__, build_skill, doctor, join, settings


def main(argv=None):
    parser = argparse.ArgumentParser(prog="v2r", description="Command-line video toolbox.")
    parser.add_argument("--version", action="version", version=f"v2r {__version__}")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("doctor", help="report on the computer v2r is running on")
    join_parser = commands.add_parser("join", help="join videos into one MP4 in work/")
    join_parser.add_argument(
        "--shape",
        required=True,
        choices=list(settings.SHAPES),
        help=" or ".join(f"{name} ({w}x{h})" for name, (w, h) in settings.SHAPES.items()) + "; there is no default",
    )
    join_parser.add_argument("videos", nargs="+", type=Path, help="video files, in the order to join them")
    commands.add_parser("build-skill", help="build skill/vid2reel.zip for uploading to Claude")
    args = parser.parse_args(argv)

    if args.command == "doctor":
        doctor.run()
    elif args.command == "join":
        try:
            print(join.join(args.videos, args.shape))
        except subprocess.CalledProcessError:
            print("v2r join: FFmpeg failed; its error is shown above.", file=sys.stderr)
            return 1
    elif args.command == "build-skill":
        print(build_skill.build())
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
