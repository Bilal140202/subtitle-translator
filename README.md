# Stable Multilingual Subtitle Translator

Optimized **faster-whisper** setup for:
- Mixed-language videos
- Better sync (VAD filter + timestamp tuning)
- Reduced hallucinations/repetition (repetition penalty, no-speech threshold)
- Automatic English translation

## Quick Start

```bash
# Activate the virtual environment (first time setup)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate English subtitles (translate mode)
python generate_subtitles.py path/to/video.mp4

# Generate subtitles in original language (transcribe mode)
python generate_subtitles.py path/to/video.mp4 --task transcribe

# Use a smaller/faster model
python generate_subtitles.py path/to/video.mp4 --model medium

# Custom output path
python generate_subtitles.py path/to/video.mp4 -o output.srt
```

## Supported Models

| Model      | VRAM   | Speed | Accuracy |
|------------|--------|-------|----------|
| tiny       | ~1 GB  | Fast  | Low      |
| base       | ~1 GB  | Fast  | Low-Med  |
| small      | ~2 GB  | Medium| Medium   |
| medium     | ~5 GB  | Medium| High     |
| large-v3   | ~10 GB | Slow  | Best     |

## Options

| Flag           | Default     | Description                                      |
|----------------|-------------|--------------------------------------------------|
| `--model, -m`  | `large-v3`  | Whisper model size                               |
| `--task, -t`   | `translate` | `translate` (to English) or `transcribe`         |
| `--output, -o` | auto        | Output SRT path (default: same name as video)    |

## How It Works

1. Loads a faster-whisper model (CTranslate2 optimized)
2. Runs VAD-based voice activity detection to skip silence
3. Transcribes with beam search (beam_size=5, best_of=5)
4. Applies anti-hallucination filters (compression ratio, log prob, no-speech thresholds)
5. Outputs a clean `.srt` file with tuned timestamps

## Requirements

- Python 3.9+
- ffmpeg (system package)
- See `requirements.txt` for Python dependencies