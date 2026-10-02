# Talking Animals Video Kit

Two parts in this repo:

1. **Animal Studio** (the app, runs on your PC). Type what happens in a scene, pick the seconds, record your own voice for each line, and it builds the video.
2. **The manual kit** (docs and templates), if you prefer to use online tools by hand. See further below.

## Animal Studio: run on your Windows PC

**Needs:** Windows, **Python 3.12 (64-bit)**, an NVIDIA GPU (works with under 12GB VRAM), about 15GB free disk for the model.

1. Double-click `setup.bat` once (creates a virtual environment, installs PyTorch with CUDA and the other packages).
2. Double-click `run.bat`. Your browser opens the app.
3. Create a project and choose 9:16 or 16:9.
4. Add scenes. You can add one of the 20 ready jungle ideas from the sidebar, or an empty scene and type your own, for example *"Lion walking in jungle, all other animals nearby"*.
5. Pick the animals, background, lighting and **how many seconds** the scene should last.
6. Press **Generate clip**.
7. Add dialogue lines, for example monkey: "Kaha ja rahe re?". **Record your voice** with the mic button (or upload a file) for each line.
8. Press **Build scene with voices**, then **Build full video**. The result is saved in `projects/<name>/final/`.

### Video generators
- **Placeholder** makes an instant test pattern. Use it to try the whole app (scenes, recording, joining) in seconds.
- **LTX-Video (local GPU)** makes the real clips. The first run downloads the model (several GB). Settings in the sidebar:
  - *Max seconds per generated part*: lower uses less VRAM.
  - *Quality steps*: more is better but slower.

### Things to know
- Clips are generated small (320x512 or 512x320) and scaled up to 720x1280 or 1280x720. Expect a soft look. This is the price of fitting under 12GB.
- A scene longer than one part (default 4s) is made by chaining parts: each new part starts from the last frame of the previous one. Faces and animals can drift a little between parts. Short scenes (4-6s) look best, then cut between scenes.
- The animals' mouths are **not** lip-synced. Your voice plays over the clip. Works best with the animal in a wide or side view; for talking shots, keep the lines short.
- **Animal voice effect** changes the pitch and speed of your voice per animal (deeper for the lion, higher for the monkey). Untick it per line to keep your natural voice. Edit the numbers in `animal_studio/data/characters.json`.
- To add an animal, background or jungle idea, edit the JSON files in `animal_studio/data/`.
- If a scene's voice is longer than its clip, the last frame is held until the voice ends.

### I only see colour bars, no animals
That is the Placeholder test clip. In the sidebar, set **Video generator** to **LTX-Video (real animals, local GPU)** and press Generate clip again. The first time it downloads the model, which takes a while.

### Not yet tested on a real GPU
The app, voice effects, scene joining and the placeholder backend are tested (`python -m unittest discover -s tests`). The LTX-Video backend was written against the `diffusers` API but I could not run it on a GPU here, so the first run on your PC may need a small fix. If it errors, send me the message.

---

# The manual kit (online tools by hand)

A reusable kit for making videos where animals (monkey, dog, lion, chimpanzee, and later pigeon and others) talk in their own voices. Scenes are set in the jungle or in the city.

This is a manual, tool-by-tool kit: documents and fill-in templates, no code. For each new video you change only the **scenario**, the **dialogue** and the **background**. The characters, voices and motions stay the same.

## Quick start

1. Copy `templates/scenario.md` and fill it in (story, language, format, setting, cast).
2. Copy `templates/shot-list.md` and split the story into shots of about 5-10 seconds.
3. For each shot, fill in `templates/prompt-card.md` using:
   - `characters/character-bible.md` for the animal's look and voice
   - `library/motions.md` for the movement (walk, run, climb, fly, bark)
   - `library/backgrounds.md` for the jungle or city setting
4. Follow `docs/01-workflow.md` to generate images, video, voices and lip-sync, then edit.
5. Export as 9:16 (vertical) or 16:9 (horizontal). See `docs/03-vertical-vs-horizontal.md`.

## What is in the kit

| Path | Purpose |
|------|---------|
| `docs/01-workflow.md` | The 7-step process and a per-video checklist |
| `docs/02-tools.md` | Tool categories and what to look for in each |
| `docs/03-vertical-vs-horizontal.md` | Settings for 9:16 and 16:9 |
| `docs/04-hindi-english-voices.md` | Choosing and keeping voices, Hindi vs English |
| `characters/character-bible.md` | Fixed look, personality and voice for each animal |
| `library/motions.md` | Motion prompts per animal |
| `library/backgrounds.md` | Jungle and city background prompts |
| `library/sound-effects.md` | Sound effects list |
| `templates/` | Blank scenario, shot list and prompt card |
| `examples/` | Two fully worked examples |

## Adding a new animal

Add an entry to `characters/character-bible.md` (copy the blank entry at the bottom) and add its movements to `library/motions.md`. Nothing else changes.

## The one rule for consistency

Generate each animal's reference image **once** and reuse it in every shot. Use the same voice for that animal in every video. This is what makes viewers recognise the characters.
