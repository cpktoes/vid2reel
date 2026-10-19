"""The sound half of `render`: the sound bed, each shot's own sound kept or silent, to the exact sample.

A picture frame is a whole number of samples (1600 at 48 kHz and 30 frames a second), so a shot's sound is cut by
sample count and every shot's sound is exactly as long as its picture.
"""

from pathlib import Path

from v2r import settings
from v2r.render import plan, video


def samples_per_frame():
    """Samples of sound in one picture frame; ValueError when the sound rate is not a whole multiple of the frame rate."""
    if settings.AUDIO_RATE % settings.OUTPUT_FPS:
        raise ValueError("The sound rate is not a whole number of samples per picture frame.")
    return settings.AUDIO_RATE // settings.OUTPUT_FPS


def mix_command(the_plan, work_dir, output):
    """The one FFmpeg command that builds the sound bed (a float WAV) of the whole reel into `output`.

    The inputs are the working copies of the shots whose sound is kept, read over the same stretch as their picture.
    A working copy always carries stereo AAC (normalize adds silence where a clip had none), so no other case exists.
    """
    per_frame = samples_per_frame()
    rate = settings.AUDIO_RATE
    form = f"aformat=sample_fmts=fltp:sample_rates={rate}:channel_layouts=stereo"
    inputs, branches, labels = [], [], []
    kept = 0  # inputs given so far
    for index, segment in enumerate(the_plan["segments"]):
        length = segment["frames"] * per_frame
        if segment["sound"] == "keep":
            _, skip = plan.seek(segment["start_frame"])
            seek, window = video.source_window(segment, the_plan)
            source = Path(work_dir).resolve() / segment["working"]
            inputs += ["-ss", f"{seek:.6f}", "-t", f"{window:.6f}", "-i", str(source)]
            kept += 1
            branches.append(
                f"[{kept - 1}:a]atrim=start_sample={skip * per_frame}:end_sample={skip * per_frame + length},"
                f"asetpts=N/{rate}/TB,{form},apad=whole_len={length},atrim=end_sample={length}[s{index}]")
        else:
            branches.append(f"anullsrc=r={rate}:cl=stereo,atrim=end_sample={length},{form}[s{index}]")
        labels.append(f"[s{index}]")
    branches.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1[bed]")
    return [
        *video.QUIET, "-y",
        *inputs,
        "-filter_complex", ";".join(branches),
        "-map", "[bed]", "-c:a", "pcm_f32le", "-ar", str(rate), "-ac", "2",
        str(output),
    ]
