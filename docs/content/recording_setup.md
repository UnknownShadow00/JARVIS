# Recording Setup Checklist

## OBS Scenes

- `Scene 1 - Main Build View`: desktop capture full screen with webcam picture-in-picture in the lower-right corner.
- `Scene 2 - Face Cam Intro`: webcam larger on screen for the first 30 to 60 seconds while the repo or logo sits behind it.
- `Scene 3 - Full Screen Demo`: desktop only, no webcam, for terminal demos and code walkthroughs.
- `Scene 4 - Vertical Shorts`: 1080x1920 canvas with cropped desktop center, large captions, and webcam at the top or bottom.
- `Scene 5 - Thumbnail Capture`: clean dark desktop background, repo or terminal open, one strong hero frame for still grabs.

## Audio

- Microphone: Blue Yeti on cardioid mode.
- Gain: keep hardware gain low to medium; avoid clipping and bring level up in OBS or post.
- Distance: 6 to 10 inches from mouth, slightly off-axis to reduce plosives.
- Sample rate: `48 kHz`.
- OBS filters:
- `Noise Suppression`: RNNoise or equivalent light suppression.
- `Noise Gate`: close around `-40 dB`, open around `-32 dB` as a starting point.
- `Compressor`: mild compression around `3:1` so narration stays even.
- `Limiter`: cap peaks around `-3 dB`.
- Monitoring check: record 20 seconds before every session and verify no hum, clipping, or keyboard dominance.

## Lighting

- Key light at 45 degrees to the face, slightly above eye line.
- Fill light or bounced light on the opposite side to soften shadows.
- Background light in blue or cyan to match the JARVIS tone.
- Keep monitor brightness below face light so skin tone stays readable.
- Avoid mixed color temperatures; keep lights consistent.

## Thumbnail Template

- Dark background with black, graphite, or deep navy tones.
- Arc reactor glow effect behind the subject, monitor, or title block.
- Bold text overlay with 3 to 5 words max, such as `REAL JARVIS BRAIN` or `LOCAL AI JARVIS`.
- One dominant focal point: your face reacting, terminal reply, or glowing interface.
- Secondary visual: code editor or waveform, but never clutter the frame.
- Use bright cyan or white text with strong contrast and a subtle outer glow.

## Upload Checklist

### Title Format

- YouTube long-form: `Building a Real JARVIS from Scratch - Part X: [Topic]`
- Shorts/TikTok cut: `I Built Tony Stark AI That Runs FREE on My PC`

### Description Template

```md
Building a real local-first JARVIS from scratch.

Repo:
https://github.com/UnknownShadow00/JARVIS

Episode playlist:
[add playlist link]

Follow the build:
[add TikTok link]
[add X link]

Stack in this episode:
- FastAPI
- Ollama
- Qwen3
- Gemma

#LocalAI #JARVIS #Ollama #FastAPI #Python #AITools
```

### Tags

- `JARVIS`
- `local AI`
- `Ollama`
- `FastAPI`
- `Qwen3`
- `Gemma`
- `Python AI assistant`
- `Tony Stark AI`
- `offline AI`
- `AI automation`

### Final Pre-Publish Check

- Confirm title matches episode number and topic.
- Confirm GitHub link works.
- Confirm first line of description explains the value fast.
- Add chapter markers for YouTube when applicable.
- Export captions or verify auto-captions are accurate.
- Check thumbnail readability on mobile.
- Pin a top comment with repo link and next-episode teaser.
