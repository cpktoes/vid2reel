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

# doctor
NETWORK_TIMEOUT = 5  # seconds to wait for github.com / pypi.org to answer
