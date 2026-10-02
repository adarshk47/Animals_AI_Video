"""Animal Studio: run with `streamlit run app.py`."""
import streamlit as st

from animal_studio import pipeline
from animal_studio.config import load_json
from animal_studio.generator import get_backend
from animal_studio.project import Line, Project, Scene, safe_name
from animal_studio.prompts import build_prompt

st.set_page_config(page_title="Animal Studio", page_icon="🦁", layout="wide")

CHARS = load_json("characters.json")
BGS = load_json("backgrounds.json")
LIGHTS = load_json("lighting.json")
SCENARIOS = load_json("scenarios.json")
ANIMALS = list(CHARS)


def animal_label(k):
    return CHARS[k]["label"]


@st.cache_resource
def backend_cache():
    return {}


def backend_for(name, segment, steps):
    cache = backend_cache()
    key = (name, segment, steps)
    if key not in cache:
        cache.clear()  # keep only one model in memory
        cache[key] = get_backend(name, segment_seconds=segment, steps=steps) if name == "ltx" \
            else get_backend(name)
    return cache[key]


# ---------------- sidebar: project + settings ----------------
st.sidebar.title("🦁 Animal Studio")
names = Project.list_names()
choice = st.sidebar.selectbox("Project", ["➕ New project"] + names)
if choice == "➕ New project":
    new_name = st.sidebar.text_input("New project name", "my_jungle_video")
    orient = st.sidebar.radio("Format", ["vertical", "horizontal"], horizontal=True,
                              format_func=lambda x: "9:16 Shorts" if x == "vertical" else "16:9 YouTube")
    if st.sidebar.button("Create project", type="primary"):
        pr = Project(name=safe_name(new_name), orientation=orient)
        pr.save()
        st.rerun()
    st.title("Create a project to begin")
    st.write("Pick a name and format in the sidebar.")
    st.stop()

project = Project.load(choice)

st.sidebar.divider()
def has_gpu() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


BACKENDS = ["placeholder", "ltx"]
backend_name = st.sidebar.radio(
    "Video generator", BACKENDS, index=1 if has_gpu() else 0,
    format_func=lambda x: "Placeholder (colour-bar TEST clip)" if x == "placeholder"
    else "LTX-Video (real animals, local GPU)")
if backend_name == "placeholder":
    st.sidebar.warning("Test mode: clips will be colour bars, not animals. "
                       "Choose LTX-Video for real clips.")
seg = st.sidebar.slider("Max seconds per generated part", 2.0, 6.0, 4.0, 0.5,
                        help="Lower uses less VRAM. Longer scenes are chained from several parts.")
steps = st.sidebar.slider("Quality steps", 10, 50, 30,
                          help="More steps = better but slower.")
orient_new = st.sidebar.radio("Format", ["vertical", "horizontal"],
                              index=["vertical", "horizontal"].index(project.orientation), horizontal=True)
if orient_new != project.orientation:
    project.orientation = orient_new
    project.save()
    st.sidebar.warning("Format changed: regenerate the clips.")

st.sidebar.divider()
st.sidebar.subheader("Add scene from jungle ideas")
idea = st.sidebar.selectbox("Idea", range(len(SCENARIOS)), format_func=lambda i: SCENARIOS[i]["title"])
sc_idea = SCENARIOS[idea]
st.sidebar.caption(sc_idea["prompt"])
if st.sidebar.button("Add this idea"):
    project.scenes.append(Scene(
        title=sc_idea["title"], prompt=sc_idea["prompt"], animals=sc_idea["animals"],
        background=sc_idea["background"], lighting=sc_idea.get("lighting", "day"),
        duration=sc_idea["duration"],
        lines=[Line(speaker=s, text=t) for s, t in sc_idea["lines"]]))
    project.save()
    st.rerun()
if st.sidebar.button("Add empty scene"):
    project.scenes.append(Scene(title=f"Scene {len(project.scenes) + 1}", animals=["lion"]))
    project.save()
    st.rerun()

# ---------------- main: scenes ----------------
st.title(f"Project: {project.name}")
st.caption(f"{'9:16 vertical' if project.orientation == 'vertical' else '16:9 horizontal'} · "
           f"{len(project.scenes)} scene(s)")

if not project.scenes:
    st.info("Add a scene from the sidebar to start.")

for idx, sc in enumerate(project.scenes):
    with st.expander(f"Scene {idx + 1}: {sc.title}  ·  {sc.duration}s", expanded=(idx == 0)):
        c1, c2 = st.columns([3, 2])
        with c1:
            sc.title = st.text_input("Title", sc.title, key=f"t{sc.id}")
            sc.prompt = st.text_area(
                "What happens in this scene (the video prompt)", sc.prompt, key=f"p{sc.id}", height=90,
                placeholder="Lion walking in the jungle, all other animals nearby")
            sc.animals = st.multiselect("Animals in the scene", ANIMALS, sc.animals,
                                        format_func=animal_label, key=f"a{sc.id}")
            b1, b2, b3 = st.columns(3)
            bg_keys = list(BGS)
            sc.background = b1.selectbox("Background", bg_keys, bg_keys.index(sc.background)
                                         if sc.background in bg_keys else 0,
                                         format_func=lambda k: BGS[k]["label"], key=f"b{sc.id}")
            l_keys = list(LIGHTS)
            sc.lighting = b2.selectbox("Lighting", l_keys, l_keys.index(sc.lighting)
                                       if sc.lighting in l_keys else 0, key=f"l{sc.id}")
            sc.duration = b3.slider("Seconds", 2, 30, sc.duration, key=f"d{sc.id}")
            sc.seed = st.number_input("Seed (change for a different take)", 0, 999999, sc.seed,
                                      key=f"s{sc.id}")
            with st.popover("See the full prompt sent to the model"):
                st.write(build_prompt(sc))
        with c2:
            if sc.clip and project.path(sc.clip).exists():
                st.video(str(project.path(sc.clip)))
            else:
                st.info("No clip yet.")
            if backend_name == "placeholder":
                st.warning("Test mode: this makes colour bars, not animals. "
                           "Switch the Video generator in the sidebar to LTX-Video.")
            if st.button("🎬 Generate clip", key=f"g{sc.id}", type="primary"):
                bar = st.progress(0.0, text="Starting...")
                try:
                    be = backend_for(backend_name, seg, steps)
                    pipeline.generate_clip(project, sc, be,
                                           lambda f, m: bar.progress(min(f, 1.0), text=m))
                    project.save()
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        st.markdown("**Dialogue** (record your own voice for each line, or upload a file)")
        for li, ln in enumerate(sc.lines):
            d1, d2, d3, d4 = st.columns([1.3, 3, 2.5, 0.6])
            ln.speaker = d1.selectbox("Who", ANIMALS, ANIMALS.index(ln.speaker)
                                      if ln.speaker in ANIMALS else 0,
                                      format_func=animal_label, key=f"sp{ln.id}")
            ln.text = d2.text_area("Line (script for you to read)", ln.text, key=f"tx{ln.id}", height=68)
            with d3:
                rec = st.audio_input("Record", key=f"rec{ln.id}")
                up = st.file_uploader("or upload", type=["wav", "mp3", "m4a", "ogg"],
                                      key=f"up{ln.id}", label_visibility="collapsed")
                src = up or rec
                if src is not None:
                    (project.dir / "voices").mkdir(parents=True, exist_ok=True)
                    ext = (src.name.rsplit(".", 1)[-1] if "." in src.name else "wav")
                    rel = f"voices/{ln.id}.{ext}"
                    project.path(rel).write_bytes(src.getvalue())
                    if ln.audio != rel:
                        ln.audio = rel
                        sc.scene_video = None
                if ln.audio and project.path(ln.audio).exists():
                    st.audio(str(project.path(ln.audio)))
                ln.apply_effect = st.checkbox("Animal voice effect", ln.apply_effect, key=f"fx{ln.id}")
            if d4.button("🗑", key=f"dl{ln.id}"):
                sc.lines.pop(li)
                project.save()
                st.rerun()
        if st.button("➕ Add line", key=f"al{sc.id}"):
            sc.lines.append(Line(speaker=sc.animals[0] if sc.animals else "lion"))
            project.save()
            st.rerun()

        e1, e2, e3, e4 = st.columns(4)
        if e1.button("🎞 Build scene with voices", key=f"bs{sc.id}"):
            try:
                pipeline.build_scene(project, sc)
                project.save()
                st.rerun()
            except Exception as e:
                st.error(str(e))
        if e2.button("⬆ Move up", key=f"up_{sc.id}", disabled=idx == 0):
            project.scenes[idx - 1], project.scenes[idx] = project.scenes[idx], project.scenes[idx - 1]
            project.save()
            st.rerun()
        if e3.button("⬇ Move down", key=f"dn_{sc.id}", disabled=idx == len(project.scenes) - 1):
            project.scenes[idx + 1], project.scenes[idx] = project.scenes[idx], project.scenes[idx + 1]
            project.save()
            st.rerun()
        if e4.button("🗑 Delete scene", key=f"ds_{sc.id}"):
            project.scenes.pop(idx)
            project.save()
            st.rerun()
        if sc.scene_video and project.path(sc.scene_video).exists():
            st.video(str(project.path(sc.scene_video)))
    project.save()

st.divider()
if project.scenes and st.button("🎥 Build full video", type="primary"):
    try:
        with st.spinner("Joining scenes..."):
            out = pipeline.build_full_video(project)
            project.save()
        st.success(f"Saved: {out}")
        st.video(str(out))
        st.download_button("Download video", out.read_bytes(), file_name=out.name, mime="video/mp4")
    except Exception as e:
        st.error(str(e))
