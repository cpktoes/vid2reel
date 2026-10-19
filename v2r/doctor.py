"""`v2r doctor`: a plain-English report on the computer v2r is running on."""

import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from v2r import ROOT, settings

ENCODERS = {"libx264": "H.264 video encoder", "aac": "AAC audio encoder", "pcm_f32le": "32-bit float WAV sound encoder"}
FILTERS = [
    "scale", "crop", "zscale", "tonemap", "loudnorm", "drawtext",
    "format", "fps", "setsar", "setpts", "loop", "transpose", "hflip", "vflip", "aresample", "apad", "anullsrc",
    # the filters `v2r look` measures with (fps and scale are listed above)
    "select", "signalstats", "blurdetect", "scdet", "deshake", "ebur128", "metadata", "ametadata",
    # the filters `v2r render` builds with (the others it uses are listed above)
    "trim", "atrim", "asetpts", "aformat", "perspective", "lutyuv", "setparams", "concat", "sine", "afade", "aevalsrc",
    "amultiply", "amix", "volume",
]
DECODERS = ["hevc", "h264", "aac", "mjpeg", "png", "pcm_f32le"]
# names exactly as FFmpeg's -muxers and -demuxers lists print them
MUXERS = ["mp4", "matroska", "wav"]
DEMUXERS = ["concat", "matroska,webm", "wav", "image2", "mov,mp4,m4a,3gp,3g2,mj2"]
HOSTS = ["github.com", "pypi.org"]
GB = 1e9


def run():
    print("v2r doctor: a report on this computer\n")

    ffmpeg = tool_version("ffmpeg")
    ffprobe = tool_version("ffprobe")
    print(f"FFmpeg {ffmpeg} is installed." if ffmpeg else "FFmpeg is NOT installed.")
    print(f"ffprobe {ffprobe} is installed." if ffprobe else "ffprobe is NOT installed.")
    if ffmpeg:
        encoders = ffmpeg_names("-encoders")
        for name, what in ENCODERS.items():
            print(f"The {what} ({name}) is {'available' if name in encoders else 'MISSING'}.")
        filters = ffmpeg_names("-filters")
        for name in FILTERS:
            print(f"The {name} filter is {'available' if name in filters else 'MISSING'}.")
        decoders = ffmpeg_names("-decoders")
        for name in DECODERS:
            print(f"The {name} decoder is {'available' if name in decoders else 'MISSING'}.")
        muxers = ffmpeg_names("-muxers")
        for name in MUXERS:
            print(f"The {name} muxer is {'available' if name in muxers else 'MISSING'}.")
        demuxers = ffmpeg_names("-demuxers")
        for name in DEMUXERS:
            print(f"The {name} demuxer is {'available' if name in demuxers else 'MISSING'}.")
    else:
        print("Encoders, filters, decoders, muxers and demuxers can't be checked without FFmpeg.")

    print(f"Python is version {platform.python_version()}.")
    cpus = os.process_cpu_count()
    print(f"This computer has {cpus} processor{'' if cpus == 1 else 's'}." if cpus else "The number of processors is unknown.")
    print(f"{shutil.disk_usage(ROOT).free / GB:.1f} GB of disk space is free.")
    memory = free_memory()
    print(f"{memory / GB:.1f} GB of memory is free." if memory is not None else "Free memory can't be measured here.")

    for host in HOSTS:
        problem = reach(host)
        print(f"{host} can be reached." if problem is None else f"{host} can NOT be reached ({problem}).")


def tool_version(tool):
    """The version an FFmpeg tool reports, or None if it isn't installed."""
    if shutil.which(tool) is None:
        return None
    first_line = subprocess.run([tool, "-version"], capture_output=True, text=True).stdout.split("\n", 1)[0]
    match = re.search(r"version (\S+)", first_line)  # "ffmpeg version 8.0.1 Copyright ..."
    return match.group(1) if match else "(unknown version)"


def ffmpeg_names(option):
    """The names in FFmpeg's `-encoders`, `-decoders`, `-filters`, `-muxers` or `-demuxers` list."""
    out = subprocess.run(["ffmpeg", "-hide_banner", option], capture_output=True, text=True).stdout
    return {line.split()[1] for line in out.splitlines() if len(line.split()) > 1}


def missing_ffmpeg_features(encoders=None, filters=None, decoders=None, *, muxers=None, demuxers=None):
    """Plain phrases for every FFmpeg piece named that this computer lacks; empty if none.

    Each argument is a list of names to check. When the caller names no list at all, all of doctor's own are checked:
    ENCODERS, FILTERS, DECODERS, MUXERS and DEMUXERS, read at call time. When the caller names any encoder, filter or
    decoder list (normalize does), a muxer or demuxer list left out means none, so a caller that never asked for muxers
    is never held to them. Up to five local FFmpeg calls, no network.
    """
    if shutil.which("ffmpeg") is None:
        return ["FFmpeg"]
    if shutil.which("ffprobe") is None:
        return ["ffprobe"]
    everything = encoders is None and filters is None and decoders is None and muxers is None and demuxers is None
    encoders = list(ENCODERS) if encoders is None else encoders
    filters = FILTERS if filters is None else filters
    decoders = DECODERS if decoders is None else decoders
    muxers = (MUXERS if everything else []) if muxers is None else muxers
    demuxers = (DEMUXERS if everything else []) if demuxers is None else demuxers
    have_encoders = ffmpeg_names("-encoders")
    have_filters = ffmpeg_names("-filters")
    have_decoders = ffmpeg_names("-decoders")
    missing = [
        f"the {ENCODERS[name]} ({name})" if name in ENCODERS else f"the {name} encoder"
        for name in encoders if name not in have_encoders
    ]
    missing += [f"the {name} filter" for name in filters if name not in have_filters]
    missing += [f"the {name} decoder" for name in decoders if name not in have_decoders]
    if muxers:
        have_muxers = ffmpeg_names("-muxers")
        missing += [f"the {name} muxer" for name in muxers if name not in have_muxers]
    if demuxers:
        have_demuxers = ffmpeg_names("-demuxers")
        missing += [f"the {name} demuxer" for name in demuxers if name not in have_demuxers]
    return missing


def free_memory():
    """Bytes of memory free for new work, or None if it can't be measured."""
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():  # Linux
        free = int(re.search(r"MemAvailable:\s+(\d+) kB", meminfo.read_text()).group(1)) * 1024
        # Inside a container, the container's own limit can be lower than the machine's.
        try:
            limit = Path("/sys/fs/cgroup/memory.max").read_text().strip()
            used = int(Path("/sys/fs/cgroup/memory.current").read_text())
            if limit != "max":
                free = min(free, int(limit) - used)
        except (OSError, ValueError):
            pass
        return free
    if sys.platform == "darwin":  # macOS: total memory times the percentage it says is available
        out = subprocess.run(["sysctl", "-n", "hw.memsize", "kern.memorystatus_level"], capture_output=True, text=True).stdout
        total, percent = map(int, out.split())
        return total * percent // 100
    return None


def reach(host):
    """None if https://<host> answers, otherwise a short reason why not."""
    request = urllib.request.Request(f"https://{host}", method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=settings.NETWORK_TIMEOUT):
            return None
    except urllib.error.HTTPError:
        return None  # it answered, even if with an error page
    except OSError as error:
        return str(getattr(error, "reason", error))
