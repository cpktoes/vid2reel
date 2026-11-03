"""Entry point for `python3 -m v2r` and the `v2r` command."""

import argparse
import subprocess
import sys
from pathlib import Path

from v2r import __version__, build_skill, doctor, join, look, normalize, render, settings


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
    normalize_parser.add_argument(
        "--work", type=str, default=None,  # text, not a Path: Path("") would quietly become the current folder
        help="the work folder for the working copies and manifest.json; leave out for work/ in this repo; "
             "the last job it holds is cleared first, and a folder with lettered files but no manifest.json is refused",
    )
    normalize_parser.add_argument(
        "--no-size-limit", action="store_true", default=False,
        help="include a file over the phone's size cap; for a computer only, never from a phone",
    )
    look_parser = commands.add_parser(
        "look", help="make contact sheets and measurements of the working copies in work/", allow_abbrev=False)
    look_parser.add_argument(
        "folder", nargs="?", type=Path, default=None,
        help="the work folder that holds manifest.json; leave out for work/ in this repo",
    )
    look_parser.add_argument(
        "--work", type=Path, default=None,
        help="the work folder that holds manifest.json; leave out for work/ in this repo",
    )
    for name, text in (
        ("check", "check a cut list against the work folder; prints one sentence per problem"),
        ("render", "build the reel a cut list describes, in work/"),
    ):
        cut_parser = commands.add_parser(name, help=text, allow_abbrev=False)
        cut_parser.add_argument(
            "cutlist", nargs="?", type=Path, default=None,
            help="the cut list; leave out for cutlist.json in the work folder",
        )
        cut_parser.add_argument(
            "--work", type=Path, default=None,
            help="the work folder that holds manifest.json; leave out for work/ in this repo",
        )
    match_parser = commands.add_parser(
        "match", help="write a mild touch-up for each clip into the cut list, from look.json", allow_abbrev=False)
    match_parser.add_argument(
        "cutlist", nargs="?", type=Path, default=None,
        help="the cut list; leave out for cutlist.json in the work folder",
    )
    match_parser.add_argument(
        "--work", type=Path, default=None,
        help="the work folder that holds manifest.json and look.json; leave out for work/ in this repo",
    )
    revise_common = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    revise_common.add_argument(
        "--cutlist", type=Path, default=None,
        help="the cut list to change; leave out for cutlist.json in the work folder",
    )
    revise_common.add_argument(
        "--work", type=Path, default=None,
        help="the work folder that holds manifest.json; leave out for work/ in this repo",
    )
    revise_parser = commands.add_parser(
        "revise", help="make one named change to a cut list and save it as a new numbered list beside it; never renders",
        allow_abbrev=False)
    changes = revise_parser.add_subparsers(dest="change", required=True, metavar="CHANGE")
    sound_parser = changes.add_parser(
        "sound", parents=[revise_common], allow_abbrev=False,
        help="keep or mute every shot's own sound, or one shot's with --shot")
    sound_parser.add_argument("setting", choices=["keep", "off"], help="keep the shots' own sound, or turn it off")
    sound_parser.add_argument(
        "--shot", default=None, metavar="N",  # text: revise checks it, so a bad one gets a plain sentence, not usage text
        help="change only this shot, counted from 1 in list order; leave out for every shot",
    )
    canvas_parser = changes.add_parser(
        "canvas", parents=[revise_common], allow_abbrev=False,
        help="make the list tall or wide; only the canvas size changes")
    canvas_parser.add_argument("shape", choices=list(settings.SHAPES), help="the shape the list should have")
    reorder_parser = changes.add_parser(
        "reorder", parents=[revise_common], allow_abbrev=False,
        help="play the shots in a new order, every shot number once, such as 3,1,2; start with a shot by putting it first")
    reorder_parser.add_argument("order", metavar="ORDER", help="the shot numbers in their new order, such as 3,1,2")
    drop_parser = changes.add_parser(
        "drop", parents=[revise_common], allow_abbrev=False,
        help="take out every shot of a clip (drop C) or one shot (drop shot 3)")
    drop_parser.add_argument(
        "what", nargs="+", metavar="WHAT",  # revise reads the words, so a wrong one gets a plain sentence, not usage text
        help="a clip letter such as C, or the word shot and a number such as shot 3")
    shorter_parser = changes.add_parser(
        "shorter", parents=[revise_common], allow_abbrev=False,
        help="trim the shots named in --from, in that order, from their ends, to reach --to seconds")
    shorter_parser.add_argument("--to", required=True, metavar="SECONDS", help="the length to aim for, such as 15")
    shorter_parser.add_argument(
        "--from", dest="shots", required=True, metavar="SHOTS",  # "from" is a Python keyword; text, so revise can answer in a sentence
        help="the shots to trim, weakest first, counted from 1 in list order, such as 6,2")
    commands.add_parser("build-skill", help="build skill/vid2reel.zip for uploading to Claude", allow_abbrev=False)
    args = parser.parse_args(argv)
    try:
        return run(args, parser)
    except Exception as error:  # the last resort: whatever was not foreseen is one plain sentence, never a Python traceback
        detail = normalize.clean_text(f"{type(error).__name__}: {error}", settings.ERROR_DETAIL_CHARS)
        print(f"v2r {args.command}: something unexpected went wrong ({detail}).", file=sys.stderr)
        return 1


def run(args, parser):
    """Do the command `args` names and return its exit code; the errors each command expects are answered here."""
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
        if args.work is not None and not args.work.strip():
            print("v2r normalize: --work needs a folder name; leave it out to use work/ in this repo.", file=sys.stderr)
            return 1
        try:
            manifest = normalize.normalize(
                args.files, args.shape, None if args.work is None else Path(args.work), size_limit=not args.no_size_limit)
        except normalize.NormalizeError as error:
            print(f"v2r normalize: {error}", file=sys.stderr)
            return 1
        return 0 if any(clip["status"] == "done" for clip in manifest["clips"]) else 1
    elif args.command == "look":
        if args.folder is not None and args.work is not None and args.folder.resolve() != args.work.resolve():
            print("v2r look: the work folder was named twice, once on its own and once after --work, "
                  "and the two differ; name it once.", file=sys.stderr)
            return 1
        try:
            result = look.look(args.work if args.work is not None else args.folder)
        except look.LookError as error:
            print(f"v2r look: {error}", file=sys.stderr)
            return 1
        return 0 if any(clip["status"] == "done" for clip in result["clips"]) else 1
    elif args.command == "check":
        checked = render.check.check(args.cutlist, args.work)
        for line in render.check.report(checked):
            print(line)
        return 1 if checked.problems else 0
    elif args.command == "render":
        try:
            reel, sentences = render.render(args.cutlist, args.work)
        except render.RenderError as error:
            print(f"v2r render: {error}", file=sys.stderr)
            return 1
        for sentence in sentences:
            print(sentence)
        print(reel)
    elif args.command == "match":
        try:
            _, lines = render.match.match(args.cutlist, args.work)
        except render.match.MatchError as error:
            print(f"v2r match: {error}", file=sys.stderr)
            return 1
        for line in lines:
            print(line)
    elif args.command == "revise":
        options = {name: value for name, value in vars(args).items() if name not in ("command", "change", "cutlist", "work")}
        try:
            _, lines, ready = render.revise.run(args.change, options, args.cutlist, args.work)
        except render.revise.ReviseError as error:
            print(f"v2r revise: {error}", file=sys.stderr)
            return 1
        for line in lines:
            print(line)
        return 0 if ready else 1
    elif args.command == "build-skill":
        print(build_skill.build())
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
