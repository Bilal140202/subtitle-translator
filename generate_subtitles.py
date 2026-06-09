import os
import datetime
import argparse
from faster_whisper import WhisperModel


def format_timestamp(seconds: float):
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int(td.microseconds / 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}'


def generate_subtitles(input_video: str, output_srt: str = None,
                       model_size: str = 'large-v3', task: str = 'translate'):
    """
    Generate subtitles from a video file using faster-whisper.

    Timing: Uses raw whisper segment timestamps with a small 50ms lead-in
    for natural reading. No overlaps — each subtitle starts only after
    the previous one ends.

    Args:
        input_video: Path to the input video file
        output_srt:  Path for the output SRT file (default: same name .srt)
        model_size:  Whisper model size
        task:        'translate' (to English) or 'transcribe' (keep original)
    """
    if not output_srt:
        output_srt = input_video.rsplit('.', 1)[0] + '.srt'

    if input_video.lower().endswith('.srt'):
        print('Error: Please choose a video file, not an SRT file.')
        return False

    if not os.path.exists(input_video):
        print(f'Error: File not found: {input_video}')
        return False

    device = 'cpu'
    compute_type = 'int8'

    print(f'Device: {device}')
    print(f'Compute type: {compute_type}')
    print(f'Loading model: {model_size} ...')

    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    print(f'Running task: {task} ...')

    segments, info = model.transcribe(
        input_video,
        task=task,
        beam_size=5,
        best_of=5,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=300,
            speech_pad_ms=200,
        ),
        word_timestamps=True,
        condition_on_previous_text=False,
        temperature=0.0,
        compression_ratio_threshold=2.2,
        log_prob_threshold=-1.0,
        no_speech_threshold=0.6,
        repetition_penalty=1.2,
    )

    print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
    print(f'Saving subtitles to: {output_srt}')

    # Collect all segments first, then fix overlaps
    raw_segments = []
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        raw_segments.append({
            'start': segment.start,
            'end': segment.end,
            'text': text,
        })

    # Fix timing: small lead-in, enforce no overlaps, minimum duration
    LEAD_IN = 0.05          # 50ms before speech starts
    MIN_DURATION = 0.8      # minimum 800ms per subtitle
    MIN_GAP = 0.15          # 150ms gap between subtitles

    prev_end = 0.0
    count = 0
    with open(output_srt, 'w', encoding='utf-8') as f:
        for seg in raw_segments:
            start = max(prev_end + MIN_GAP, seg['start'] - LEAD_IN)
            end = seg['end']

            # Enforce minimum duration
            if end - start < MIN_DURATION:
                end = start + MIN_DURATION

            text = seg['text']

            f.write(f'{count + 1}\n')
            f.write(f'{format_timestamp(start)} --> {format_timestamp(end)}\n')
            f.write(f'{text}\n\n')
            count += 1
            prev_end = end

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