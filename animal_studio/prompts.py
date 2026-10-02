"""Turn a short scene description into a full prompt for the video model.

The video model reads only the first 128 tokens (about 65 words), so the most
important parts come first and optional parts are dropped when over budget.
"""
from .config import STYLE_SUFFIX, load_json

MAX_WORDS = 65


def _words(text: str) -> int:
    return len(text.split())


def build_prompt_info(scene, characters=None, backgrounds=None, lighting=None,
                      max_words: int = MAX_WORDS):
    """Return (prompt, dropped) where dropped lists the parts left out."""
    characters = characters or load_json("characters.json")
    backgrounds = backgrounds or load_json("backgrounds.json")
    lighting = lighting or load_json("lighting.json")

    head = scene.prompt.strip().rstrip(".")
    bg = backgrounds.get(scene.background)
    setting = ("Setting: " + bg["prompt"]) if bg else ""
    light = lighting.get(scene.lighting, "")
    looks = [characters[a]["look"] for a in scene.animals if a in characters]

    # Optional parts, most expendable last in this list.
    shown_looks = list(looks)
    style = STYLE_SUFFIX

    def assemble():
        animals = ("Animals: " + "; ".join(shown_looks)) if shown_looks else ""
        return ". ".join(p for p in (head, setting, light, animals, style) if p)

    dropped = []
    if _words(assemble()) > max_words and style:
        style = "photorealistic, cinematic"  # shorter style first
        dropped.append("style shortened")
    while _words(assemble()) > max_words and len(shown_looks) > 2:
        shown_looks.pop()
        dropped.append("an animal description")
    if _words(assemble()) > max_words and style:
        style = ""
        dropped.append("style words")
    while _words(assemble()) > max_words and shown_looks:
        shown_looks.pop()
        dropped.append("an animal description")
    return assemble(), dropped


def build_prompt(scene, characters=None, backgrounds=None, lighting=None) -> str:
    return build_prompt_info(scene, characters, backgrounds, lighting)[0]
