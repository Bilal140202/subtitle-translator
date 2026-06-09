import os
import sys
import argparse
import subprocess
import shlex


def burn_subtitles(
    input_video: str,
    input_srt: str,
    output_video: str = None,
    font_name: str = 'Liberation Sans',
    font_size: int = 22,
    margin_v: int = 35,
):
    """
    Burn styled subtitles into a video using ffmpeg.

    Style: Clean sans-serif font, white text, dark outline + shadow,
    bottom-center alignment with semi-transparent background box.

    Args:
        input_video:  Path to source video
        input_srt:    Path to .srt subtitle file
        output_video: Path for output video (default: <input>_subtitled.mp4)
        font_name:    Font family name (must be installed on system)
        font_size:    Font size in points
        margin_v:     Bottom margin in pixels
    """
    if not output_video:
        base = input_video.rsplit('.', 1)[0]
        output_video = f'{base}_subtitled.mp4'

    if not os.path.exists(input_video):
        print(f'Error: Video not found: {input_video}')
        return False
    if not os.path.exists(input_srt):
        print(f'Error: SRT not found: {input_srt}')
        return False

    # ASS-style force_style string
    # Alignment 2 = bottom-center
    # BorderStyle 3 = opaque box behind text
    # colours are &HBBGGRR (BGR, not RGB)
    style = (
        f'FontName={font_name},'
        f'FontSize={font_size},'
        f'PrimaryColour=&H00FFFFFF,'       # white text
        f'SecondaryColour=&H00FFFFFF,'
        f'OutlineColour=&H00000000,'        # black outline
        f'BackColour=&H80000000,'           # 50% transparent black box
        f'Bold=1,'
        f'Italic=0,'
        f'Underline=0,'
        f'StrikeOut=0,'
        f'ScaleX=100,'
        f'ScaleY=100,'
        f'Spacing=2,'
        f'Angle=0,'
        f'BorderStyle=3,'                   # opaque box
        f'Outline=0,'                       # no extra outline (box handles contrast)
        f'Shadow=0,'
        f'Alignment=2,'                     # bottom center
        f'MarginL=40,'
        f'MarginR=40,'
        f'MarginV={margin_v},'
        f'Encoding=1'
    )

    # Escape special characters for ffmpeg filter
    escaped_srt = input_srt.replace("'", "'\\''").replace(":", "\\:")

    cmd = [
        'ffmpeg', '-y',
        '-i', input_video,
        '-vf', f"subtitles='{escaped_srt}':force_style='{style}'",
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '18',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-movflags', '+faststart',
        output_video
    ]

    print(f'Burning subtitles into: {output_video}')
    print(f'Font: {font_name} Bold, Size: {font_size}, Margin: {margin_v}px')
    print(f'Running ffmpeg...\n')

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f'FFmpeg error:\n{result.stderr[-2000:]}')
        return False

    size_mb = os.path.getsize(output_video) / (1024 * 1024)
    print(f'\nDone! Output: {output_video} ({size_mb:.1f} MB)')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Burn styled subtitles into a video')
    parser.add_argument('input_video', help='Path to the input video file')
    parser.add_argument('input_srt', help='Path to the .srt subtitle file')
    parser.add_argument('--output', '-o', help='Output video path (default: <name>_subtitled.mp4)')
    parser.add_argument('--font', default='Liberation Sans', help='Font name (default: Liberation Sans)')
    parser.add_argument('--font-size', type=int, default=22, help='Font size in points (default: 22)')
    parser.add_argument('--margin', type=int, default=35, help='Bottom margin in pixels (default: 35)')

    args = parser.parse_args()

    burn_subtitles(
        input_video=args.input_video,
        input_srt=args.input_srt,
        output_video=args.output,
        font_name=args.font,
        font_size=args.font_size,
        margin_v=args.margin,
    )