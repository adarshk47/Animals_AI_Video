"""Turn a short scene description into a full prompt for the video model."""
from .config import STYLE_SUFFIX, load_json


def build_prompt(scene, characters=None, backgrounds=None, lighting=None) -> str:
    characters = characters or load_json("characters.json")
    backgrounds = backgrounds or load_json("backgrounds.json")
    lighting = lighting or load_json("lighting.json")

    parts = [scene.prompt.strip().rstrip(".")]
    looks = [characters[a]["look"] for a in scene.animals if a in characters]
    if looks:
        parts.append("The animals: " + "; ".join(looks))
    bg = backgrounds.get(scene.background)
    if bg:
        parts.append("Setting: " + bg["prompt"])
    light = lighting.get(scene.lighting)
    if light:
        parts.append(light)
    parts.append(STYLE_SUFFIX)
    return ". ".join(p for p in parts if p)
