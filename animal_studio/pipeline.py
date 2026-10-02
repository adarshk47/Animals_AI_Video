"""High-level actions used by the UI: generate clip, build scene, build full video."""
from pathlib import Path
from typing import List, Optional

from . import compose
from .config import GEN_SIZE, OUTPUT_SIZE, load_json
from .generator import Progress
from .project import Project, Scene
from .prompts import build_prompt


def generate_clip(project: Project, scene: Scene, backend, progress: Progress = None) -> Path:
    (project.dir / "clips").mkdir(parents=True, exist_ok=True)
    out = project.path(f"clips/{scene.id}.mp4")
    prompt = build_prompt(scene)
    backend.generate(prompt, scene.duration, GEN_SIZE[project.orientation],
                     scene.seed, out, progress)
    scene.clip = f"clips/{scene.id}.mp4"
    scene.scene_video = None  # needs rebuilding
    return out


def build_scene(project: Project, scene: Scene) -> Path:
    """Mux the scene clip with your recorded voice lines."""
    if not scene.clip or not project.path(scene.clip).exists():
        raise RuntimeError("Generate the clip for this scene first.")
    characters = load_json("characters.json")
    work = project.dir / "work"
    work.mkdir(parents=True, exist_ok=True)

    processed: List[Path] = []
    for ln in scene.lines:
        if not ln.audio or not project.path(ln.audio).exists():
            continue
        dst = work / f"{scene.id}_{ln.id}.wav"
        ch = characters.get(ln.speaker, {})
        if ln.apply_effect:
            compose.process_voice(project.path(ln.audio), dst,
                                  ch.get("pitch", 0), ch.get("speed", 1.0))
        else:
            compose.process_voice(project.path(ln.audio), dst, 0, 1.0)
        processed.append(dst)

    voice: Optional[Path] = None
    if processed:
        voice = work / f"{scene.id}_voice.wav"
        compose.build_voice_track(processed, voice)

    out_dir = project.dir / "scenes"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{scene.id}.mp4"
    compose.make_scene(project.path(scene.clip), voice, out, OUTPUT_SIZE[project.orientation])
    scene.scene_video = f"scenes/{scene.id}.mp4"
    return out


def build_full_video(project: Project) -> Path:
    files = []
    for s in project.scenes:
        if not s.scene_video or not project.path(s.scene_video).exists():
            build_scene(project, s)
        files.append(project.path(s.scene_video))
    if not files:
        raise RuntimeError("No scenes to join.")
    out_dir = project.dir / "final"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{project.name}.mp4"
    compose.concat_scenes(files, out)
    return out
