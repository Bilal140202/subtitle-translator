import os
import sys
import argparse
import subprocess


def burn_subtitles(
    input_video: str,
    input_srt: str,
    output_video: str = None,
    font_name: str = 'Montserrat Bold',
    font_size: int = 24,
    bar_height: int = 60,
    outline_width: int = 3,
    margin_v: int = 12,
    bitrate: str = '2200k',
):
    """
    Burn styled subtitles into a video using ffmpeg.

    Style: White text with thick black outline on a fixed black bar
    added at the bottom of the video (does not crop original content).

    Args:
        input_video:  Path to source video
        input_srt:    Path to .srt subtitle file
        output_video: Path for output video (default: <input>_subtitled.mp4)
        font_name:    Font family name (must be installed on system)
        font_size:    Font size in points
        bar_height:   Height of the black bar added at bottom in pixels
        outline_width: Thickness of the black text outline in points
        margin_v:     Bottom margin within the black bar in pixels
        bitrate:      Video bitrate (e.g. '2200k', '4000k')
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
    # Alignment 2 = bottom-center (fixed position)
    # BorderStyle 1 = outline + drop shadow
    # Colours are &HAABBGGRR (alpha + BGR, not RGB)
    style = (
        f'FontName={font_name},'
        f'FontSize={font_size},'
        f'PrimaryColour=&H00FFFFFF,'       # white text
        f'SecondaryColour=&H00FFFFFF,'
        f'OutlineColour=&H00000000,'        # black outline
        f'BackColour=&H00000000,'           # black (used by shadow)
        f'Bold=1,'
        f'Italic=0,'
        f'Underline=0,'
        f'StrikeOut=0,'
        f'ScaleX=100,'
        f'ScaleY=100,'
        f'Spacing=2,'
        f'Angle=0,'
        f'BorderStyle=1,'                   # outline mode (black stroke)
        f'Outline={outline_width},'         # thick black outline
        f'Shadow=0,'
        f'Alignment=2,'                     # bottom center — fixed position
        f'MarginL=50,'
        f'MarginR=50,'
        f'MarginV={margin_v},'
        f'Encoding=1'
    )

    # Video filter: pad black bar at bottom, then burn subtitles on it
    vf = (
        f"pad=iw:ih+{bar_height}:0:0:black,"
        f"subtitles='{input_srt}':force_style='{style}'"
    )

    cmd = [
        'ffmpeg', '-nostdin', '-y',
        '-i', input_video,
        '-vf', vf,
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-b:v', bitrate,
        '-maxrate', bitrate,
        '-bufsize', '4000k',
        '-c:a', 'aac',
        '-b:a', '96k',
        '-movflags', '+faststart',
        output_video
    ]

    print(f'Burning subtitles into: {output_video}')
    print(f'Font: {font_name}, Size: {font_size}pt')
    print(f'Style: White text + {outline_width}px black outline on {bar_height}px black bar')
    print(f'Bitrate: {bitrate}')
    print(f'Running ffmpeg...\n')

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f'FFmpeg error:\n{result.stderr[-2000:]}')
        return False

    size_mb = os.path.getsize(output_video) / (1024 * 1024)
    print(f'\nDone! Output: {output_video} ({size_mb:.1f} MB)')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Burn styled subtitles into a video with black bar')
    parser.add_argument('input_video', help='Path to the input video file')
    parser.add_argument('input_srt', help='Path to the .srt subtitle file')
    parser.add_argument('--output', '-o', help='Output video path (default: <name>_subtitled.mp4)')
    parser.add_argument('--font', default='Montserrat Bold', help='Font name (default: Montserrat Bold)')
    parser.add_argument('--font-size', type=int, default=24, help='Font size in points (default: 24)')
    parser.add_argument('--bar-height', type=int, default=60, help='Black bar height in pixels (default: 60)')
    parser.add_argument('--outline', type=int, default=3, help='Black outline thickness in points (default: 3)')
    parser.add_argument('--margin', type=int, default=12, help='Bottom margin in black bar (default: 12)')
    parser.add_argument('--bitrate', default='2200k', help='Video bitrate e.g. 2200k, 4000k (default: 2200k)')

    args = parser.parse_args()

    burn_subtitles(
        input_video=args.input_video,
        input_srt=args.input_srt,
        output_video=args.output,
        font_name=args.font,
        font_size=args.font_size,
        bar_height=args.bar_height,
        outline_width=args.outline,
        margin_v=args.margin,
        bitrate=args.bitrate,
    )