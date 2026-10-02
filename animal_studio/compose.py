"""ffmpeg helpers: voice effects, voice track, scene muxing, final concat."""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from .config import FPS, SAMPLE_RATE


def ffmpeg_exe() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:  # pragma: no cover
        raise RuntimeError("ffmpeg not found. Install ffmpeg or `pip install imageio-ffmpeg`.") from e


def run(args: List[str]) -> str:
    p = subprocess.run([ffmpeg_exe(), "-y", "-hide_banner", *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg failed:\n" + p.stderr[-2000:])
    return p.stderr


def duration(path) -> float:
    """Media duration in seconds (parsed from `ffmpeg -i`, so no ffprobe needed)."""
    p = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", p.stderr)
    if not m:
        raise RuntimeError(f"Could not read duration of {path}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def voice_filter(pitch: float, speed: float) -> str:
    """Change pitch by `pitch` semitones; `speed` is tempo (1.0 = unchanged)."""
    pitch = max(-12.0, min(12.0, pitch))
    f = 2 ** (pitch / 12)
    tempo = max(0.5, min(2.0, speed / f))  # asetrate shifts tempo by f; undo it
    return (f"aresample={SAMPLE_RATE},asetrate={SAMPLE_RATE * f:.2f},"
            f"aresample={SAMPLE_RATE},atempo={tempo:.4f}")


def process_voice(src, dst, pitch: float = 0, speed: float = 1.0) -> None:
    run(["-i", str(src), "-vn", "-af", voice_filter(pitch, speed),
         "-ar", str(SAMPLE_RATE), "-ac", "2", str(dst)])


def build_voice_track(files: List[Path], out: Path, gap: float = 0.4) -> float:
    """Concatenate voice lines with a short gap between; returns total length."""
    if not files:
        raise ValueError("no voice files")
    inputs, chains = [], []
    for i, f in enumerate(files):
        inputs += ["-i", str(f)]
        chains.append(f"[{i}:a]aresample={SAMPLE_RATE},aformat=channel_layouts=stereo,"
                      f"apad=pad_dur={gap}[a{i}]")
    labels = "".join(f"[a{i}]" for i in range(len(files)))
    fc = ";".join(chains) + f";{labels}concat=n={len(files)}:v=0:a=1[out]"
    run([*inputs, "-filter_complex", fc, "-map", "[out]", str(out)])
    return duration(out)


def make_scene(clip, voice_track: Optional[Path], out, size: Tuple[int, int],
               min_seconds: float = 0) -> None:
    """Scale the clip, add the voice track (silence if none) and hold the last
    frame if the voice is longer than the clip."""
    w, h = size
    vlen = duration(clip)
    alen = duration(voice_track) if voice_track else 0
    total = max(vlen, alen, min_seconds)
    extra = max(0.0, total - vlen)
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
          f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p")
    if extra > 0.01:
        vf += f",tpad=stop_mode=clone:stop_duration={extra:.3f}"
    audio_in = (["-i", str(voice_track)] if voice_track
                else ["-f", "lavfi", "-i", f"anullsrc=r={SAMPLE_RATE}:cl=stereo"])
    run(["-i", str(clip), *audio_in, "-map", "0:v", "-map", "1:a",
         "-vf", vf, "-af", f"aresample={SAMPLE_RATE},apad",
         "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
         "-c:a", "aac", "-b:a", "160k", "-ar", str(SAMPLE_RATE), "-ac", "2", str(out)])


def concat_scenes(scene_files: List[Path], out) -> None:
    """Join already-uniform scene files (all made by make_scene)."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        for p in scene_files:
            f.write(f"file '{Path(p).resolve().as_posix()}'\n")
        listfile = f.name
    try:
        run(["-f", "concat", "-safe", "0", "-i", listfile, "-c", "copy", str(out)])
    finally:
        Path(listfile).unlink(missing_ok=True)
