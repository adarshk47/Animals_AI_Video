# Workflow: from scenario to finished video

Seven steps. Do steps 3-6 once per shot, then step 7 once per video.

## 1. Write the scenario
Fill in `templates/scenario.md`. Decide language, format (9:16 or 16:9), setting and cast. Keep the first videos short with two animals.

## 2. Split into shots
Fill in `templates/shot-list.md`. One shot is about 5-10 seconds because AI video tools make short clips.
- Mark each shot `TALK` or `ACTION`.
- Alternate between speakers by cutting between two close-ups. This is easier than getting two animals to talk in one clip.

## 3. Generate the animal images
- Generate each animal once from its look prompt in `characters/character-bible.md`. Keep the best image as the **reference image**.
- For each shot, generate an image of the animal in the background for that shot, using the reference image where the tool allows it.
- Use the right aspect ratio from the start (9:16 or 16:9).

## 4. Generate the video clips
- Use image-to-video: upload the shot image and paste the motion prompt from `library/motions.md`.
- Generate 2-3 versions and keep the best.
- Check that the animal still looks like its reference.

## 5. Generate the voices
- For each dialogue line, paste the text into a text-to-speech tool using the animal's chosen voice.
- Download one audio file per line, named by shot.
- See `04-hindi-english-voices.md` for Hindi vs English tips.

## 6. Lip-sync (TALK shots only)
- Upload the clip and the audio to a lip-sync tool.
- If the face is not detected, regenerate the clip with a closer face shot.
- Some video tools generate speech and mouth movement together; if you use one, skip steps 5-6 for those shots, but then check that the voice matches the character.

## 7. Edit and export
In a video editor:
1. Place clips in shot order.
2. Add background ambience (jungle or city) under everything.
3. Add sound effects (roar, bark, wings) on ACTION shots.
4. Add light background music, quiet under speech.
5. Add subtitles (Hindi or English).
6. Export at 9:16 or 16:9.

## Per-video checklist
- [ ] Scenario, shot list done
- [ ] Reference images saved for all animals in this video
- [ ] All shot images generated
- [ ] All clips generated and checked for consistency
- [ ] All voice files generated
- [ ] TALK shots lip-synced
- [ ] Ambience, SFX, music added; speech is clearly audible
- [ ] Subtitles added and spell-checked
- [ ] Exported in the right aspect ratio
- [ ] Licences for music and SFX checked

## Common problems
| Problem | Fix |
|---------|-----|
| Animal looks different in each shot | Use the reference image in every shot; keep the look prompt identical |
| Weird extra legs or limbs in motion | Simplify to one action, regenerate, try a different camera |
| Mouth does not match audio | Use a closer face shot; shorter lines; try another lip-sync tool |
| Text appears in the video | Add "no text, no subtitles" to the prompt |
| Clip too short for a line | Split the line, or cut to a reaction shot while the voice continues |
