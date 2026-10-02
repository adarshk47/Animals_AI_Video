"""Video generation backends.

- PlaceholderBackend: instant dummy clip (ffmpeg test pattern). Use it to try the
  whole app (dialogue, recording, editing) without waiting for the GPU.
- LTXBackend: local text-to-video with the open LTX-Video model via diffusers,
  tuned for GPUs under 12GB (CPU offload, small resolution, short segments).
  Scenes longer than one segment are made by chaining segments: each next segment
  starts from the last frame of the previous one (image-to-video).
"""
import gc
import math
import os
from pathlib import Path
from typing import Callable, Optional, Tuple

from .compose import run
from .config import DEFAULT_MODEL, FPS, LOW_GEN_SIZE, NEGATIVE_PROMPT

Progress = Optional[Callable[[float, str], None]]


def frames_for(seconds: float, fps: int = FPS) -> int:
    """LTX needs num_frames = 8k + 1."""
    k = max(1, round(seconds * fps / 8))
    return 8 * k + 1


def cuda_help(torch) -> str:
    """Explain why CUDA is unavailable, with the exact fix."""
    ver, cuda = torch.__version__, torch.version.cuda
    head = f"No CUDA GPU usable by PyTorch. (torch {ver}, built for CUDA: {cuda})\n\n"
    if cuda is None:
        return head + (
            "Cause: the CPU-only PyTorch is installed. Fix, in the project folder:\n"
            "  .venv\\Scripts\\activate\n"
            "  pip uninstall -y torch torchvision torchaudio\n"
            "  pip install torch --index-url https://download.pytorch.org/whl/cu124\n"
            "Then close this app completely and start run.bat again.")
    return head + (
        "PyTorch has CUDA support, but cannot see the GPU. Update the NVIDIA driver, "
        "restart the PC, and check that `nvidia-smi` works. Then restart run.bat.")


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
    """Low-memory LTX-Video, built for small GPUs (4GB VRAM) and 8-16GB RAM.

    1. The huge T5 text encoder is loaded alone, used once to encode the prompt on
       the CPU, then deleted. It is never in memory together with the video model.
    2. The video model is loaded without a text encoder and run with sequential CPU
       offload (one layer on the GPU at a time): slow, but needs very little VRAM.
    3. Resolution is small, so the VAE and activations stay tiny.
    """
    name = "ltx"

    def __init__(self, model_id: str = DEFAULT_MODEL, segment_seconds: float = 4.0,
                 steps: int = 30):
        self.model_id = model_id
        self.segment_seconds = segment_seconds
        self.steps = steps
        self._t2v = None
        self._i2v = None

    @staticmethod
    def low_vram_size(size: Tuple[int, int]) -> Tuple[int, int]:
        w, h = size
        return LOW_GEN_SIZE["vertical" if h > w else "horizontal"]

    def _dtype(self, torch):
        name = os.environ.get("ANIMAL_DTYPE", "bfloat16")  # set to float16 if you get black/NaN video
        return getattr(torch, name)

    def _encode_prompt(self, torch, prompt: str):
        """Load only the text encoder, encode, free it. Returns CPU tensors."""
        from diffusers import LTXPipeline
        tp = LTXPipeline.from_pretrained(self.model_id, transformer=None, vae=None,
                                         torch_dtype=self._dtype(torch))
        with torch.no_grad():
            pe, pm, ne, nm = tp.encode_prompt(
                prompt, negative_prompt=NEGATIVE_PROMPT, do_classifier_free_guidance=True,
                device="cpu")
        out = tuple(t.detach().cpu() for t in (pe, pm, ne, nm))
        del tp
        gc.collect()
        return out

    def _load_video_model(self, torch):
        if self._t2v is not None:
            return
        from diffusers import LTXImageToVideoPipeline, LTXPipeline
        if not torch.cuda.is_available():
            raise RuntimeError(cuda_help(torch))
        self._t2v = LTXPipeline.from_pretrained(
            self.model_id, text_encoder=None, tokenizer=None, torch_dtype=self._dtype(torch))
        self._i2v = LTXImageToVideoPipeline.from_pipe(self._t2v)
        self._t2v.enable_sequential_cpu_offload()  # lowest VRAM
        self._t2v.vae.enable_tiling()

    def generate(self, prompt: str, seconds: float, size: Tuple[int, int],
                 seed: int, out: Path, progress: Progress = None) -> None:
        import torch
        from diffusers.utils import export_to_video
        if not torch.cuda.is_available():
            raise RuntimeError(cuda_help(torch))
        try:
            if progress:
                progress(0.0, "Reading the prompt (text model, first time is slow)...")
            pe, pm, ne, nm = self._encode_prompt(torch, prompt)
            if progress:
                progress(0.05, "Loading the video model...")
            self._load_video_model(torch)

            w, h = self.low_vram_size(size)
            n_seg = max(1, math.ceil(seconds / self.segment_seconds))
            seg_frames = frames_for(min(seconds, self.segment_seconds))
            dev = "cuda"
            embeds = dict(prompt_embeds=pe.to(dev), prompt_attention_mask=pm.to(dev),
                          negative_prompt_embeds=ne.to(dev), negative_prompt_attention_mask=nm.to(dev))
            all_frames, last = [], None
            for i in range(n_seg):
                if progress:
                    progress(0.1 + 0.85 * i / n_seg, f"Generating part {i + 1}/{n_seg} (slow on small GPUs)")
                gen = torch.Generator("cpu").manual_seed(seed + i)
                kwargs = dict(width=w, height=h, num_frames=seg_frames, frame_rate=FPS,
                              num_inference_steps=self.steps, generator=gen, **embeds)
                if last is None:
                    frames = self._t2v(**kwargs).frames[0]
                else:
                    frames = self._i2v(image=last, **kwargs).frames[0]
                last = frames[-1]
                all_frames.extend(frames[1:] if all_frames else frames)
            export_to_video(all_frames, str(out), fps=FPS)
        except torch.cuda.OutOfMemoryError as e:
            torch.cuda.empty_cache()
            raise RuntimeError("GPU ran out of memory. Lower 'Max seconds per generated part' "
                               "in the sidebar (try 2) and close other programs.") from e
        if progress:
            progress(1.0, "done")


def get_backend(name: str, **kw):
    if name == "ltx":
        return LTXBackend(**kw)
    return PlaceholderBackend()
