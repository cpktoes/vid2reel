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

# doctor
NETWORK_TIMEOUT = 5  # seconds to wait for github.com / pypi.org to answer

# Phone limits, measured in Claude's cloud workspace on 2026-10-12 (see docs/phone-limits.md)
MAX_ATTACHMENT_BYTES = 320 * 1000**2  # one attached file: 80% of the 400 MB upload warning
MAX_ATTACHMENTS = 10  # files in one message: the most tried, all arrived (a tested number, so no margin)
MAX_RESULT_BYTES = 24 * 1024**2  # a result sent back: 80% of the 30 MiB send limit
