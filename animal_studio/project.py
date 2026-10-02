"""Project data model, saved as projects/<name>/project.json."""
import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

from .config import PROJECTS_DIR


def _uid() -> str:
    return uuid.uuid4().hex[:8]


@dataclass
class Line:
    speaker: str = "lion"
    text: str = ""
    audio: Optional[str] = None  # path relative to the project folder (your recorded voice)
    apply_effect: bool = True    # change pitch/speed to suit the animal
    id: str = field(default_factory=_uid)


@dataclass
class Scene:
    title: str = "New scene"
    prompt: str = ""
    animals: List[str] = field(default_factory=list)
    background: str = "dense_jungle"
    lighting: str = "day"
    duration: int = 6            # seconds the scene should last
    seed: int = 0
    clip: Optional[str] = None   # generated silent clip, relative path
    scene_video: Optional[str] = None  # clip + voices, relative path
    lines: List[Line] = field(default_factory=list)
    id: str = field(default_factory=_uid)


@dataclass
class Project:
    name: str
    orientation: str = "vertical"   # or "horizontal"
    scenes: List[Scene] = field(default_factory=list)

    @property
    def dir(self) -> Path:
        return PROJECTS_DIR / self.name

    def path(self, rel: str) -> Path:
        return self.dir / rel

    def save(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        with open(self.dir / "project.json", "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, name: str) -> "Project":
        with open(PROJECTS_DIR / name / "project.json", encoding="utf-8") as f:
            d = json.load(f)
        scenes = []
        for s in d.get("scenes", []):
            lines = [Line(**ln) for ln in s.pop("lines", [])]
            scenes.append(Scene(**s, lines=lines))
        return cls(name=d["name"], orientation=d.get("orientation", "vertical"), scenes=scenes)

    @staticmethod
    def list_names() -> List[str]:
        if not PROJECTS_DIR.exists():
            return []
        return sorted(p.parent.name for p in PROJECTS_DIR.glob("*/project.json"))


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip()).strip("_") or "project"
