import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__file__).resolve().parent / "data"
PROJECTS_DIR = ROOT / "projects"

# Output (final video) size per orientation.
OUTPUT_SIZE = {"vertical": (720, 1280), "horizontal": (1280, 720)}
# Generation size per orientation (small so it fits in <12GB VRAM; multiples of 32).
GEN_SIZE = {"vertical": (320, 512), "horizontal": (512, 320)}
FPS = 24
SAMPLE_RATE = 44100

DEFAULT_MODEL = "Lightricks/LTX-Video"
STYLE_SUFFIX = ("photorealistic, natural fur texture, cinematic lighting, "
                "realistic animal movement, high detail")
NEGATIVE_PROMPT = "worst quality, blurry, distorted, extra limbs, deformed, text, watermark, subtitles"


def load_json(name: str):
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)
