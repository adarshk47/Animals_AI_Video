# Prompt Card: Shot [#]

Fill each field by copying from the library, then paste into the tools. Fields are separate so you can swap one without touching the others.

## Fields
- **Shot type:** TALK / ACTION
- **Format:** 9:16 / 16:9
- **Animal look prompt** (from `characters/character-bible.md`):
  `...`
- **Background** (from `library/backgrounds.md`):
  `...`
- **Motion** (from `library/motions.md`):
  `...`
- **Camera:** static / tracking / low angle / close-up
- **Dialogue:** NAME: "..." (language: EN / HI)
- **Voice** (from character bible): ________
- **SFX:** ________

## 1. Image prompt (paste in image generator)
```
[Animal look prompt], [pose for this shot], in [Background], [Camera framing], aspect ratio [9:16 or 16:9]
```
Attach the animal's reference image if the tool supports it.

## 2. Video prompt (paste in image-to-video tool, with the image from step 1)
```
[Motion], [Camera], [Background mood]. No text, no subtitles, no logos.
```

## 3. Voice (paste in text-to-speech)
```
[Dialogue line]
```

## 4. Lip-sync (TALK shots only)
Upload the video clip and the voice audio into the lip-sync tool.

## Output file names
`shot01_image.png`, `shot01_video.mp4`, `shot01_voice.mp3`, `shot01_final.mp4`
