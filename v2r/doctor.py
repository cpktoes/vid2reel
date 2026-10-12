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

ENCODERS = {"libx264": "H.264 video encoder", "aac": "AAC audio encoder"}
FILTERS = ["scale", "crop", "zscale", "tonemap", "loudnorm", "drawtext"]
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
    else:
        print("Encoders and filters can't be checked without FFmpeg.")

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
    """The names in FFmpeg's `-encoders` or `-filters` list."""
    out = subprocess.run(["ffmpeg", "-hide_banner", option], capture_output=True, text=True).stdout
    return {line.split()[1] for line in out.splitlines() if len(line.split()) > 1}


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
