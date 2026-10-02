import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from animal_studio import compose, config, pipeline
from animal_studio.config import load_json
from animal_studio.generator import PlaceholderBackend, frames_for
from animal_studio.project import Line, Project, Scene
from animal_studio.prompts import build_prompt


def make_tone(path, seconds=1.0, freq=440):
    compose.run(["-f", "lavfi", "-i", f"sine=frequency={freq}:duration={seconds}", str(path)])


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        config.PROJECTS_DIR = self.tmp  # isolate from real projects
        import animal_studio.project as pj
        pj.PROJECTS_DIR = self.tmp

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_data_files_consistent(self):
        chars, bgs = load_json("characters.json"), load_json("backgrounds.json")
        for sc in load_json("scenarios.json"):
            self.assertIn(sc["background"], bgs)
            for a in sc["animals"]:
                self.assertIn(a, chars)
            for sp, text in sc["lines"]:
                self.assertIn(sp, chars)
                self.assertTrue(text.isascii(), text)

    def test_prompt_contains_parts(self):
        s = Scene(prompt="Lion walking in jungle", animals=["lion", "monkey"],
                  background="river", lighting="night")
        p = build_prompt(s)
        for needle in ["Lion walking in jungle", "lion", "macaque", "river", "moonlight"]:
            self.assertIn(needle, p)

    def test_frames_for(self):
        for sec in (1, 2.5, 4, 6):
            self.assertEqual((frames_for(sec) - 1) % 8, 0)

    def test_project_roundtrip(self):
        p = Project(name="t", scenes=[Scene(title="a", lines=[Line(speaker="dog", text="hi")])])
        p.save()
        q = Project.load("t")
        self.assertEqual(q.scenes[0].lines[0].text, "hi")
        self.assertEqual(Project.list_names(), ["t"])

    def test_full_pipeline_with_voice(self):
        p = Project(name="e2e", orientation="horizontal")
        sc = Scene(title="s1", duration=2, animals=["lion"])
        make_tone(self.tmp / "v1.wav", 1.0)
        make_tone(self.tmp / "v2.wav", 2.5, 300)  # voice longer than clip
        (p.dir / "voices").mkdir(parents=True)
        shutil.copy(self.tmp / "v1.wav", p.dir / "voices/a.wav")
        shutil.copy(self.tmp / "v2.wav", p.dir / "voices/b.wav")
        sc.lines = [Line(speaker="lion", text="x", audio="voices/a.wav"),
                    Line(speaker="monkey", text="y", audio="voices/b.wav"),
                    Line(speaker="dog", text="no audio")]
        sc2 = Scene(title="silent", duration=1)
        p.scenes = [sc, sc2]
        be = PlaceholderBackend()
        for s in p.scenes:
            pipeline.generate_clip(p, s, be)
        out = pipeline.build_full_video(p)
        self.assertTrue(out.exists())
        # scene 1: 1.0+0.4 gap + 2.5+0.4 gap = 4.3s > 2s clip, so video is held to fit voice
        self.assertAlmostEqual(compose.duration(p.path(sc.scene_video)), 4.3, delta=0.15)
        self.assertAlmostEqual(compose.duration(p.path(sc2.scene_video)), 1.0, delta=0.15)
        self.assertAlmostEqual(compose.duration(out), 5.3, delta=0.3)

    def test_pitch_shift_keeps_length(self):
        make_tone(self.tmp / "a.wav", 2.0)
        for pitch in (-5, 5):
            compose.process_voice(self.tmp / "a.wav", self.tmp / "b.wav", pitch, 1.0)
            self.assertAlmostEqual(compose.duration(self.tmp / "b.wav"), 2.0, delta=0.1)


if __name__ == "__main__":
    unittest.main()
