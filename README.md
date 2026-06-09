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

Burns `.srt` subtitles into the video with a clean, professional look.

```bash
# Default styling (recommended)
python burn_subtitles.py video.mp4 video.srt

# Custom output path
python burn_subtitles.py video.mp4 video.srt -o output.mp4

# Adjust font size and bottom margin
python burn_subtitles.py video.mp4 video.srt --font-size 24 --margin 50

# Use a different font
python burn_subtitles.py video.mp4 video.srt --font "Noto Sans"
```

| Flag              | Default          | Description                              |
|-------------------|------------------|------------------------------------------|
| `--output, -o`    | `<name>_subtitled.mp4` | Output video path               |
| `--font`          | `Liberation Sans` | Font family (must be installed)       |
| `--font-size`     | `22`             | Font size in points                     |
| `--margin`        | `35`             | Bottom margin in pixels                 |

**Subtitle style:** Bold white text on a semi-transparent black background box, bottom-center aligned with comfortable margins. Uses `BorderStyle=3` (opaque box) for maximum readability on any background.

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
2. **Burning** — Uses ffmpeg + libass to render subtitles directly into the video frames with styled formatting (bold font, semi-transparent box, bottom alignment)

## Requirements

- Python 3.9+
- ffmpeg (system package, with libass support)
- See `requirements.txt` for Python dependencies