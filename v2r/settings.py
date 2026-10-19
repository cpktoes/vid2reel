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
MAX_PHOTO_PIXELS = 80_000_000  # pixels (width times height) of the largest photo that is opened; a 48 MP iPhone photo is well inside
MAX_VIDEO_SIDE = 8192  # pixels: a video frame wider or taller than this is left out (an iPhone's 4K is 3840 by 2160)
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
FFMPEG_TIMEOUT_FLOOR = 120  # seconds added to every conversion's time allowance: FFmpeg's start-up and a photo's short still
# seconds of conversion allowed per second of video before that file is left out (a hang guard, not a speed goal);
# the sandbox measured about 3.8 for 4K on its 2 processors (docs/phone-limits.md) and HDR tone-mapping is slower,
# so 10 leaves margin
FFMPEG_SECONDS_PER_SECOND = 10
ERROR_DETAIL_CHARS = 400  # characters of FFmpeg's own error text kept in a skipped entry
FILE_TEXT_CHARS = 200  # characters kept of any other text that came from inside a file or its name (a file name, a date)

# look: Stage 15's numbers. The blind test tunes them one at a time, so each stays a name of its own.
LOOK_WIDTH = 320  # pixels wide the measuring pass reads each picture; the height follows the picture
LOOK_FPS = 10  # frames a second the measuring pass reads
SUMMARY_SECONDS = 0.5  # seconds each summary entry in look.json covers
# seconds between the base stills; the first step that keeps a run within MAX_SHEETS_PER_RUN is used
STILL_INTERVAL_STEPS = [1.0, 1.5, 2.0]
MAX_SHEETS_PER_RUN = 20  # contact sheets one look run may make
MAX_CLIP_SECONDS = 3 * 60 * 60  # seconds: the longest working copy look reads; a manifest that claims more is not believed
# seconds a whole look run may take: a hang guard, not a speed goal. The phone measured about 0.5 s of work per second
# of video (docs/phone-limits.md), so this covers about an hour of footage; clips not started by then are skipped
LOOK_RUN_SECONDS = 30 * 60
SHEET_GRID = {"tall": (4, 3), "wide": (3, 4)}  # (columns, rows) of cells on a sheet: 12 stills per sheet
CELL_ASPECT = {"tall": (9, 16), "wide": (16, 9)}  # (width, height) proportion of one cell
# pixels wide a sheet is, by the stills' orientation. Claude's viewer shrinks a picture's long edge to about 1,568, so a
# tall sheet is 1192 wide and so 1568 high and is seen as made; a wide sheet stays 1950 by 1476 (only tall sheets were
# resized, 2026-10-18)
SHEET_WIDTH = {"tall": 1192, "wide": 1950}
SHEET_PADDING = 8  # pixels between cells and round the edge of a sheet
SHEET_BACKGROUND = (24, 24, 24)  # RGB, 0-255 per channel: the dark grey behind the stills
SHEET_JPEG_QUALITY = 85  # JPEG quality, 1-100, a sheet is first saved at
LABEL_FONT_SHARE = 0.07  # label text size as a share (0 to 1) of a cell's width
LABEL_PADDING = 8  # pixels of dark box round the label text
LABEL_BOX_COLOUR = (0, 0, 0)  # RGB, 0-255 per channel: the box behind a label
LABEL_TEXT_COLOUR = (255, 255, 255)  # RGB, 0-255 per channel: the label text
LABEL_DECIMALS = 1  # decimal places of seconds on a still's label and in a "sound peak at" time, such as A 03.0 (D-02)
LOOK_DECIMALS = 2  # decimal places kept for numbers in look.json
SHEET_JPEG_QUALITY_STEP = 10  # JPEG quality points taken off each time a sheet larger than SHEET_MAX_BYTES is saved again
SHEET_JPEG_QUALITY_MIN = 65  # JPEG quality, 1-100: the lowest a sheet is saved at; it is kept whatever its size
SHEET_MAX_BYTES = 1_500_000  # bytes: a sheet larger than this is saved again at lower quality
EXTRAS_SHARE = 1 / 3  # share of a clip's base stills that is the most extra stills it may add (D-17)
EXTRA_MIN_GAP = 0.3  # seconds an extra still keeps from every other still
PEAK_SPREADS = 3  # spreads (median absolute deviations): a peak stands at least this many above the clip's median
MOVEMENT_SPREAD_FLOOR = 0.5  # frame-difference units, 0-255: the smallest spread used, so a calm clip's flicker is no peak
LOUDNESS_SPREAD_FLOOR = 2.0  # LU (loudness units): the smallest spread used for loudness peaks
SCENE_THRESHOLD = 10  # scdet score, 0-100, at or above which the shot changed; FFmpeg's own default
CUT_STILL_DELAY = 0.1  # seconds after a new shot's first frame that its still is taken
LOUDNESS_DELAY = 0.1  # seconds the momentary loudness reading lags the sound
SILENCE_LUFS = -70  # LUFS: sound quieter than this counts as silence and is written null
DESHAKE_RANGE = 16  # pixels, a multiple of 16: how far deshake searches between analysed frames
DESHAKE_CONTRAST = 20  # 1-255: the contrast an 8-pixel block needs before deshake tracks it; FFmpeg's default of 125 ignores
# most of a 320-pixel tone-mapped picture and read a pan as a still camera on real clips (2026-10-18), so 20 tracks the pan
SHAKE_WINDOW_SECONDS = 1.0  # seconds: the centred average that separates a smooth pan from jitter
CAMERA_STILL_PX = 1.5  # pixels per analysed frame at LOOK_WIDTH: mean camera movement below this is a still camera
SHAKE_LIMIT_PX = 2.0  # pixels per analysed frame at LOOK_WIDTH: mean jitter at or above this is shaky
SUBJECT_MOVEMENT_MIN = 1.0  # frame-difference units, 0-255: movement at or above this with a still camera is a subject moving
# spreads (median absolute deviations of the clip's half-second blur): a half second blurrier than the median by more
# than this many is not sharp
BLUR_SPREADS = 3
BLUR_SPREAD_FLOOR = 0.05  # pixels of edge width: the smallest spread used
CANDIDATE_SECONDS = 2.0  # seconds each candidate window lasts (D-18)
CANDIDATE_STEP = 0.5  # seconds between the starts of neighbouring candidate windows
MAX_CANDIDATES = 5  # candidate moments listed per clip, at most
CANDIDATE_MAX_SECONDS = 4.0  # seconds: the longest merged candidate stretch
# share (0 to 1) of the larger movement score by which two windows may differ and still merge; never less than
# MOVEMENT_SPREAD_FLOOR
CANDIDATE_ALIKE_SHARE = 0.25
CHROMA_NEUTRAL = 128  # 8-bit code value of grey in video chroma (a fact of the format): the colour cast is the offset from it

# doctor
NETWORK_TIMEOUT = 5  # seconds to wait for github.com / pypi.org to answer

# render: Stage 16's numbers. The renderer builds exactly the cut list; these say how, never what.
RENDER_PRESEEK_FRAMES = 30  # frames: a shot's fast seek lands this many frames ahead of its first frame, so the exact trim always starts on the right one
RENDER_TAIL_FRAMES = 3  # frames read past a shot's end, so the exact trim always has its last frame
RENDER_PIECE_PRESET = "ultrafast"  # x264 speed of each shot's scratch piece
RENDER_PIECE_CRF = 10  # x264 quality of each scratch piece, lower is better; 10 is near lossless
RENDER_X264_PRESET = "medium"  # x264 speed of the finished reel; join's own default
RENDER_X264_CRF = 20  # x264 quality of the finished reel, lower is better; the bitrate ceiling from FIT_STEPS still applies
MAX_CUTLIST_BYTES = 1_000_000  # bytes: a cut list larger than this is not read
CUTLIST_ECHO_CHARS = 40  # characters: the longest piece of the list's own text a sentence repeats; longer text is cut, so a list cannot print a long instruction
CUTLIST_MAX_DIGITS = 15  # digits: the longest whole number a cut list may hold; a longer one is refused before Python turns it into a number
MOVE_AMOUNT = 0.04  # share (0 to 1) of the frame every push-in, pull-out and pan moves by, used in full
MUSIC_DROP_RAMP = 0.3  # seconds the music takes to drop before a kept-sound segment and to come back after it
FADE_IN_SECONDS = 0.5  # seconds the music fades in over when the list states none
FADE_OUT_SECONDS = 1.5  # seconds the music fades out over at the end when the list states none
LOUDNESS_TARGET = -14  # LUFS, integrated: the loudness a reel is evened to when its list states none
TRUE_PEAK_CEILING = -1  # dBTP: the evening gain stops before the loudest true peak would pass this
MIN_REEL_SECONDS = 3  # seconds: the shortest reel the checker allows
CROP_NOTE_SHARE = 0.5  # share (0 to 1) of a clip's picture below which the checker notes how little a crop keeps
MAX_SEGMENTS = 120  # segments one cut list may hold: their first and last frames fill at most MAX_SHEETS_PER_RUN proof sheets
TEST_TONE_ID = "test-tone"  # a name, not a number: the music id that stands for the generated test tone until Stage 18
TEST_TONE_HZ = 220  # hertz: the test tone's pitch
TEST_TONE_SECONDS = 300  # seconds the test tone lasts, as a track's length does
COVER_JPEG_QUALITY = 92  # JPEG quality (1 to 100) of the cover still
LUMA_RANGE = (16, 235)  # 8-bit code values of video black and white (a fact of the format): the touch-up's limits
CHROMA_RANGE = (16, 240)  # 8-bit code values of the legal colour range (a fact of the format)

# match: the touch-up's caps (D-23). They only ever nudge; halve them on sight if a touch-up reads as a filter.
TOUCH_UP_MAX_BRIGHTNESS = 8  # 8-bit code values: the most match moves a clip's brightness either way
TOUCH_UP_MAX_COLOUR = 4  # 8-bit code values: the most match moves a clip's blue or red either way
TOUCH_UP_SATURATION_MIN = 0.92  # multiplier: the least colour match leaves
TOUCH_UP_SATURATION_MAX = 1.08  # multiplier: the most colour match adds
TOUCH_UP_DECIMALS = 1  # decimal places of the brightness, blue and red numbers match writes
SATURATION_DECIMALS = 2  # decimal places of the saturation multiplier match writes

# Phone limits, measured in Claude's cloud workspace on 2026-10-12 (see docs/phone-limits.md)
MAX_ATTACHMENT_BYTES = 400 * 1000**2  # one attached file: the app warns above this, but a 408.7 MB file still arrived
MAX_ATTACHMENTS = 10  # files in one message: the most tried, all arrived (a tested number, so no margin)
MAX_RESULT_BYTES = 24 * 1024**2  # a result sent back: 80% of the 30 MiB send limit
