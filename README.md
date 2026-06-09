# Stable Multilingual Subtitle Translator

Optimized **faster-whisper** pipeline for:
- Mixed-language videos (Japanese, Korean, Hindi, Arabic, etc.)
- Better sync (VAD filter + timestamp tuning)
- Reduced hallucinations/repetition (repetition penalty, no-speech threshold)
- Automatic English translation
- **Styled subtitle burning** into video with professional formatting

## Quick Start

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Generate English subtitles from any video
python generate_subtitles.py video.mp4

# 3. (Optional) Burn subtitles into the video with styling
python burn_subtitles.py video.mp4 video.srt -o video_subtitled.mp4

# Full pipeline in one go:
python generate_subtitles.py video.mp4 -o video.srt
python burn_subtitles.py video.mp4 video.srt -o video_final.mp4
```

## Scripts

### `generate_subtitles.py` — Transcribe & Translate

Generates `.srt` subtitle files from video using faster-whisper.

```bash
# Translate to English (default)
python generate_subtitles.py video.mp4

# Keep original language
python generate_subtitles.py video.mp4 --task transcribe

# Use a faster/smaller model
python generate_subtitles.py video.mp4 --model medium

# Custom output path
python generate_subtitles.py video.mp4 -o custom.srt
```

| Flag           | Default     | Description                                       |
|----------------|-------------|---------------------------------------------------|
| `--model, -m`  | `large-v3`  | Whisper model size                                |
| `--task, -t`   | `translate` | `translate` (to English) or `transcribe`          |
| `--output, -o` | auto        | Output SRT path (default: same name as video)     |

### `burn_subtitles.py` — Embed Styled Subtitles into Video

Burns `.srt` subtitles into the video with a professional cinematic look.

```bash
# Default styling (recommended)
python burn_subtitles.py video.mp4 video.srt

# Custom output path
python burn_subtitles.py video.mp4 video.srt -o output.mp4

# Adjust font size, bar height, and outline thickness
python burn_subtitles.py video.mp4 video.srt --font-size 28 --bar-height 80 --outline 4

# Use a different font
python burn_subtitles.py video.mp4 video.srt --font "Bebas Neue"

# Higher quality (larger file)
python burn_subtitles.py video.mp4 video.srt --bitrate 4000k
```

| Flag              | Default            | Description                              |
|-------------------|--------------------|------------------------------------------|
| `--output, -o`    | `<name>_subtitled.mp4` | Output video path               |
| `--font`          | `Montserrat Bold`  | Font family (must be installed)          |
| `--font-size`     | `24`               | Font size in points                      |
| `--bar-height`    | `60`               | Black bar height at bottom in pixels     |
| `--outline`       | `3`                | Black outline thickness in points        |
| `--margin`        | `12`               | Bottom margin within black bar           |
| `--bitrate`       | `2200k`            | Video bitrate (e.g. 2200k, 4000k)        |

**Subtitle style:** Bold white text with thick black outline (stroke), fixed bottom-center position on a solid black bar appended below the video. The original video content is never cropped — the black bar is added as extra space.

## Supported Models

| Model      | VRAM   | Speed | Accuracy |
|------------|--------|-------|----------|
| tiny       | ~1 GB  | Fast  | Low      |
| base       | ~1 GB  | Fast  | Low-Med  |
| small      | ~2 GB  | Medium| Medium   |
| medium     | ~5 GB  | Medium| High     |
| large-v3   | ~10 GB | Slow  | Best     |

## How It Works

1. **Transcription** — Loads a faster-whisper model (CTranslate2 optimized), runs VAD-based voice activity detection to skip silence, transcribes with beam search (beam_size=5, best_of=5), and applies anti-hallucination filters
2. **Burning** — Uses ffmpeg + libass to render subtitles directly into the video frames. A black bar is appended at the bottom (no content is cropped), and white bold text with a thick black outline is rendered at a fixed position on the bar.

## Font Setup (first time)

The default font is **Montserrat Bold**. Install it once:

```bash
mkdir -p ~/.local/share/fonts
curl -sL https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf \
  -o ~/.local/share/fonts/Montserrat-Bold.ttf
fc-cache -f
```

## Requirements

- Python 3.9+
- ffmpeg (system package, with libass + libx264 support)
- Montserrat Bold font (or any installed font)
- See `requirements.txt` for Python dependencies