# Example: "Chhat Ki Baat" (city, horizontal 16:9, Hindi, short excerpt)

This is an excerpt of a longer video, to show the format. A full 3-minute video would add more scenes and shots.

## Scenario
- **Language:** Hindi
- **Format:** Horizontal 16:9 (full version about 3 min)
- **Setting:** City, Rooftop, then Busy street, day
- **Mood:** heartwarming

| Animal | Name | Role |
|--------|------|------|
| Dog | Moti | Friendly street dog who is lonely |
| Pigeon | Pintu | Pigeon who shows him the city from above |

**Story:** Moti is sitting alone on a rooftop. Pintu lands beside him and tells him what the city looks like from the sky. Moti is excited and barks happily.

## Dialogue (Devanagari)
```
MOTI: आज कोई दोस्त नहीं आया।
PINTU: मैं आ गया न! ऊपर से शहर देखोगे?
MOTI: मैं तो उड़ नहीं सकता!
PINTU: कोई बात नहीं, मैं तुम्हें सब बताऊँगा।
(Moti barks happily)
```

## Shot list
| # | Type | Background | Animal | Motion | Dialogue | Secs | SFX |
|---|------|------------|--------|--------|----------|------|-----|
| 1 | ACTION | Rooftop | (none) | Establishing wide shot of skyline | | 5 | city ambience |
| 2 | TALK | Rooftop | Dog | Talk | MOTI: "आज कोई दोस्त नहीं आया।" | 6 | wind |
| 3 | ACTION | Rooftop | Pigeon | Fly, then Land | | 6 | wing flaps |
| 4 | TALK | Rooftop | Pigeon | Talk | PINTU: "मैं आ गया न! ऊपर से शहर देखोगे?" | 7 | |
| 5 | TALK | Rooftop | Dog | Talk | MOTI: "मैं तो उड़ नहीं सकता!" | 5 | |
| 6 | TALK | Rooftop | Pigeon | Talk | PINTU: "कोई बात नहीं, मैं तुम्हें सब बताऊँगा।" | 7 | |
| 7 | ACTION | Rooftop | Dog | Bark | | 4 | happy bark |

## Prompt card for shot 3
- **Animal look:** `photorealistic [pigeon description from character bible]`
- **Background:** `city rooftop with water tank and clotheslines, buildings behind, skyline, bright natural daylight`
- **Motion:** `pigeon flying across the frame, wings flapping, smooth tracking shot`
- **Image prompt:** `[look], mid-flight above [background], wide shot, aspect ratio 16:9`
- **Video prompt:** `[motion]. No text, no subtitles, no logos.`

## Notes
- Add the pigeon's entry to `characters/character-bible.md` before generating (a blank entry template is at the bottom).
- Test the Hindi voice on one line first (see `docs/04-hindi-english-voices.md`).
- Moti and Pintu need clearly different voices.
- Hindi subtitles in Devanagari, bottom of the frame.
