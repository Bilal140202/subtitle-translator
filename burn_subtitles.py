import os
import re
import sys
import argparse
import subprocess


def srt_to_ass(srt_path, ass_path, width, height, font_name, font_size, outline_width, margin_v):
    """Convert SRT to ASS with explicit PlayRes matching the padded video frame.

    This ensures subtitles are position-locked to the bottom black bar
    instead of floating based on libass default resolution.
    """
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n\s*\n', content.strip())
    events = []

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        ts_line = None
        text_lines = []
        for line in lines[1:]:
            if '-->' in line:
                ts_line = line
            else:
                text_lines.append(line)
        if not ts_line or not text_lines:
            continue
        match = re.match(
            r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})',
            ts_line
        )
        if not match:
            continue

        def to_ass_time(t):
            h, m, s_ms = t.split(':')
            s, ms = s_ms.split(',')
            return f'{h}:{m}:{s}.{ms}'

        start = to_ass_time(match.group(1))
        end = to_ass_time(match.group(2))
        text = '\\N'.join(text_lines)
        events.append(f'Dialogue: 0,{start},{end},Default,,0,0,0,,{text}')

    ass_content = f"""[Script Info]
Title: Subtitles
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,2,0,1,{outline_width},0,2,50,50,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{chr(10).join(events)}
"""
    with open(ass_path, 'w', encoding='utf-8') as f:
        f.write(ass_content)

    return ass_path


def burn_subtitles(
    input_video: str,
    input_srt: str,
    output_video: str = None,
    font_name: str = 'Montserrat Bold',
    font_size: int = 24,
    bar_height: int = 60,
    outline_width: int = 3,
    margin_v: int = 10,
    bitrate: str = '2200k',
):
    """
    Burn styled subtitles into a video using ffmpeg.

    Style: White bold text with thick black outline (stroke), fixed
    bottom-center position on a solid black bar appended below the video.
    The original video content is never cropped.

    Uses SRT -> ASS conversion with PlayRes matching the padded frame
    to guarantee subtitles stay locked to the black bar.

    Args:
        input_video:  Path to source video
        input_srt:    Path to .srt subtitle file
        output_video: Path for output video (default: <input>_subtitled.mp4)
        font_name:    Font family name (must be installed on system)
        font_size:    Font size in points
        bar_height:   Height of the black bar added at bottom in pixels
        outline_width: Thickness of the black text outline in points
        margin_v:     Bottom margin within the padded frame in pixels
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

    # Get video resolution
    probe = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
         '-show_entries', 'stream=width,height', '-of', 'csv=p=0', input_video],
        capture_output=True, text=True
    )
    try:
        width, height = probe.stdout.strip().split(',')
        width, height = int(width), int(height)
    except (ValueError, AttributeError):
        print('Warning: Could not detect resolution, defaulting to 1280x720')
        width, height = 1280, 720

    padded_height = height + bar_height

    # Convert SRT to ASS with PlayRes matching the padded frame
    ass_path = input_srt.rsplit('.', 1)[0] + '.ass'
    srt_to_ass(
        input_srt, ass_path,
        width=width, height=padded_height,
        font_name=font_name, font_size=font_size,
        outline_width=outline_width, margin_v=margin_v
    )

    # Video filter: pad black bar at bottom, then burn ASS subtitles
    vf = f"pad=iw:ih+{bar_height}:0:0:black,ass='{ass_path}'"

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
    print(f'Resolution: {width}x{height} -> {width}x{padded_height}')
    print(f'Font: {font_name}, Size: {font_size}pt, Outline: {outline_width}px')
    print(f'Style: White text + black outline on {bar_height}px black bar')
    print(f'Bitrate: {bitrate}')
    print(f'Running ffmpeg...\n')

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Clean up temp ASS file
    if os.path.exists(ass_path):
        os.remove(ass_path)

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
    parser.add_argument('--margin', type=int, default=10, help='Bottom margin in padded frame (default: 10)')
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