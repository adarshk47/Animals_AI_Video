"""Video generation backends.

- PlaceholderBackend: instant dummy clip (ffmpeg test pattern). Use it to try the
  whole app (dialogue, recording, editing) without waiting for the GPU.
- LTXBackend: local text-to-video with the open LTX-Video model via diffusers,
  tuned for GPUs under 12GB (CPU offload, small resolution, short segments).
  Scenes longer than one segment are made by chaining segments: each next segment
  starts from the last frame of the previous one (image-to-video).
"""
import math
from pathlib import Path
from typing import Callable, Optional, Tuple

from .compose import run
from .config import DEFAULT_MODEL, FPS, NEGATIVE_PROMPT

Progress = Optional[Callable[[float, str], None]]


def frames_for(seconds: float, fps: int = FPS) -> int:
    """LTX needs num_frames = 8k + 1."""
    k = max(1, round(seconds * fps / 8))
    return 8 * k + 1


class PlaceholderBackend:
    name = "placeholder"

    def generate(self, prompt: str, seconds: float, size: Tuple[int, int],
                 seed: int, out: Path, progress: Progress = None) -> None:
        w, h = size
        run(["-f", "lavfi", "-i", f"testsrc2=size={w}x{h}:rate={FPS}:duration={seconds}",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)])
        if progress:
            progress(1.0, "placeholder done")


class LTXBackend:
    name = "ltx"

    def __init__(self, model_id: str = DEFAULT_MODEL, segment_seconds: float = 4.0,
                 steps: int = 30):
        self.model_id = model_id
        self.segment_seconds = segment_seconds
        self.steps = steps
        self._t2v = None
        self._i2v = None

    def _load(self):
        if self._t2v is not None:
            return
        import torch
        from diffusers import LTXImageToVideoPipeline, LTXPipeline
        if not torch.cuda.is_available():
            raise RuntimeError("No CUDA GPU found. Use the placeholder backend, or install "
                               "the CUDA build of PyTorch (see README).")
        self._t2v = LTXPipeline.from_pretrained(self.model_id, torch_dtype=torch.bfloat16)
        self._i2v = LTXImageToVideoPipeline.from_pipe(self._t2v)
        # Keep VRAM low: only the active sub-model lives on the GPU.
        self._t2v.enable_model_cpu_offload()
        self._t2v.vae.enable_tiling()

    def generate(self, prompt: str, seconds: float, size: Tuple[int, int],
                 seed: int, out: Path, progress: Progress = None) -> None:
        import torch
        from diffusers.utils import export_to_video
        self._load()
        w, h = size
        n_seg = max(1, math.ceil(seconds / self.segment_seconds))
        seg_frames = frames_for(min(seconds, self.segment_seconds))
        all_frames, last = [], None
        for i in range(n_seg):
            if progress:
                progress(i / n_seg, f"Generating part {i + 1}/{n_seg}")
            gen = torch.Generator("cpu").manual_seed(seed + i)
            kwargs = dict(prompt=prompt, negative_prompt=NEGATIVE_PROMPT, width=w, height=h,
                          num_frames=seg_frames, num_inference_steps=self.steps, generator=gen)
            if last is None:
                frames = self._t2v(**kwargs).frames[0]
            else:
                frames = self._i2v(image=last, **kwargs).frames[0]
            last = frames[-1]
            all_frames.extend(frames[1:] if all_frames else frames)
        export_to_video(all_frames, str(out), fps=FPS)
        if progress:
            progress(1.0, "done")


def get_backend(name: str, **kw):
    if name == "ltx":
        return LTXBackend(**kw)
    return PlaceholderBackend()
