import os
import sys
import datetime
import argparse
from faster_whisper import WhisperModel

# =========================
# CONFIGURATION
# =========================

def format_timestamp(seconds: float):
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int(td.microseconds / 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}'


def generate_subtitles(input_video: str, output_srt: str = None, model_size: str = 'large-v3', task: str = 'translate'):
    """
    Generate subtitles from a video file using faster-whisper.

    Args:
        input_video: Path to the input video file
        output_srt: Path for the output SRT file (default: same name as video with .srt)
        model_size: Whisper model size (tiny, base, small, medium, large-v2, large-v3)
        task: 'translate' (to English) or 'transcribe' (keep original language)
    """
    if not output_srt:
        output_srt = input_video.rsplit('.', 1)[0] + '.srt'

    if input_video.lower().endswith('.srt'):
        print('Error: Please choose a video file, not an SRT file.')
        return False

    if not os.path.exists(input_video):
        print(f'Error: File not found: {input_video}')
        return False

    # CPU-only environment -> use int8 for best performance
    device = 'cpu'
    compute_type = 'int8'

    print(f'Device: {device}')
    print(f'Compute type: {compute_type}')
    print(f'Loading model: {model_size} ...')

    model = WhisperModel(
        model_size,
        device=device,
        compute_type=compute_type
    )

    print(f'Running task: {task} ...')
    print(f'Detected language will be shown below.')

    segments, info = model.transcribe(
        input_video,
        task=task,
        beam_size=5,
        best_of=5,
        vad_filter=True,
        word_timestamps=True,
        condition_on_previous_text=False,
        temperature=0.0,
        compression_ratio_threshold=2.2,
        log_prob_threshold=-1.0,
        no_speech_threshold=0.6,
        repetition_penalty=1.2
    )

    print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
    print(f'Saving subtitles to: {output_srt}')

    count = 0
    with open(output_srt, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, start=1):
            start = max(0, segment.start - 0.10)
            end = max(start + 0.1, segment.end - 0.03)
            text = segment.text.strip()

            if not text:
                continue

            f.write(f'{i}\n')
            f.write(f'{format_timestamp(start)} --> {format_timestamp(end)}\n')
            f.write(f'{text}\n\n')
            count += 1

            if i % 25 == 0:
                print(f'  Processed {i} segments...')

    print(f'\nDone! {count} subtitle entries written.')
    print(f'Subtitle file saved at: {output_srt}')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate subtitles from video using faster-whisper')
    parser.add_argument('input_video', help='Path to the input video file')
    parser.add_argument('--output', '-o', help='Output SRT file path (default: same name .srt)')
    parser.add_argument('--model', '-m', default='large-v3',
                        help='Model size: tiny, base, small, medium, large-v2, large-v3 (default: large-v3)')
    parser.add_argument('--task', '-t', default='translate', choices=['translate', 'transcribe'],
                        help='Task: translate (to English) or transcribe (original language)')

    args = parser.parse_args()

    generate_subtitles(
        input_video=args.input_video,
        output_srt=args.output,
        model_size=args.model,
        task=args.task
    )