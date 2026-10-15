"""Every tunable number in v2r lives here.

Code elsewhere imports values from this module instead of hard-coding them,
so all knobs can be found and adjusted in one place. Give each value a
comment stating its unit (seconds, pixels, frames, dB, ...).
"""

# join: the finished video's frame, as (width, height) in pixels
SHAPES = {
    "tall": (1080, 1920),  # short-form
    "wide": (1920, 1080),  # longer-form YouTube
}
OUTPUT_FPS = 30  # frames per second

# join: fitting the result under MAX_RESULT_BYTES (below, with the phone limits)
AUDIO_BITRATE = 128_000  # bits per second of AAC sound
FIT_HEADROOM = 0.03  # share of MAX_RESULT_BYTES held back for the MP4 file's own overhead
# Frame sizes to try, largest first: a scale of the shape's full size, and the lowest
# video bitrate (bits per second) worth watching at that size.
FIT_STEPS = [
    (1, 2_500_000),  # 1080x1920 tall, 1920x1080 wide
    (2 / 3, 1_200_000),  # 720x1280 tall, 1280x720 wide
    (1 / 2, 700_000),  # 540x960 tall, 960x540 wide
]

# normalize: working size per job shape and source orientation, as (max width, max height) in pixels;
# None means no limit on that side. Nothing is ever scaled up. A square source uses the shape's own
# entry ("portrait" in a tall job, "landscape" in a wide job).
WORKING_SIZE = {
    "tall": {"portrait": (1080, 1920), "landscape": (None, 1920)},
    "wide": {"landscape": (1920, 1080), "portrait": (1920, None)},
}
# Pillow format names a photo may have; any other picture type is not opened as a photo.
# (The iPhone's JPEG variant, MPO, is opened by the JPEG reader, so it needs no entry of its own.)
PHOTO_FORMATS = ["JPEG", "PNG", "HEIF"]
PHOTO_SECONDS = 4  # seconds a photo's still clip lasts
PHOTO_JPEG_QUALITY = 92  # 1-100, quality of the upright full-size copy of a photo
X264_PRESET = "veryfast"  # working copies: fast encode (the renderer re-encodes them later)
X264_CRF = 20  # working copies: video quality, lower is better
WORKING_AUDIO_BITRATE = 160_000  # bits per second of AAC sound in a working copy
AUDIO_RATE = 48_000  # samples per second of every working copy's sound
TONEMAP = "hable"  # HDR to ordinary colour: hable, mobius or reinhard
# This pair was picked by eye from the four-panel strips on 2026-10-13. Research that day found hable at 203
# closest to Apple's own rendering of the same clips; mobius and reinhard need 800 to match that brightness, and
# 1000 is too dark with any operator. Switching is these two numbers.
TONEMAP_NPL = 203  # nits: nominal peak for HLG sources; 203 is BT.2408's HLG reference white
TONEMAP_NPL_PQ = 100  # nits: nominal peak for PQ sources
SLOW_MOTION_MIN_FPS = 100  # frames per second: a median frame rate at or above this marks slow-motion source
STEADY_TOLERANCE = 0.25  # share of the median frame gap that a frame gap may differ by and still count as steady
FFPROBE_TIMEOUT = 30  # seconds ffprobe may take to read one file's facts before that file is left out
FFMPEG_TIMEOUT = 600  # seconds FFmpeg may take to convert one file before that file is left out (a hang guard, not a speed goal)
ERROR_DETAIL_CHARS = 400  # characters of FFmpeg's own error text kept in a skipped entry
FILE_TEXT_CHARS = 200  # characters kept of any other text that came from inside a file or its name (a file name, a date)

# doctor
NETWORK_TIMEOUT = 5  # seconds to wait for github.com / pypi.org to answer

# Phone limits, measured in Claude's cloud workspace on 2026-10-12 (see docs/phone-limits.md)
MAX_ATTACHMENT_BYTES = 400 * 1000**2  # one attached file: the app warns above this, but a 408.7 MB file still arrived
MAX_ATTACHMENTS = 10  # files in one message: the most tried, all arrived (a tested number, so no margin)
MAX_RESULT_BYTES = 24 * 1024**2  # a result sent back: 80% of the 30 MiB send limit
