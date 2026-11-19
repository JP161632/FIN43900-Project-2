"""Create pitch-preserving upload copies of the combined local videos.

Personal recordings remain outside the repository. Sources are never changed.
"""
import argparse
import json
import subprocess
from pathlib import Path

FFMPEG = r'C:\ffmpeg\bin\ffmpeg.exe'
FFPROBE = r'C:\ffmpeg\bin\ffprobe.exe'


def inspect(path):
    return json.loads(subprocess.check_output([
        FFPROBE, '-v', 'error', '-show_entries',
        'stream=codec_type,width,height:format=duration', '-of', 'json', str(path)
    ], text=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, required=True)
    args = parser.parse_args()
    jobs = [(1, 1.25, 180), (2, 1.02, 300)]
    for number, rate, limit in jobs:
        source = args.folder/f'Project-2-Video-{number}-Combined-Full-Length.mp4'
        output = args.folder/f'Project-2-Video-{number}-Upload-{rate:g}x.mp4'
        if not source.is_file():
            raise FileNotFoundError(source)
        if output.exists():
            raise FileExistsError(f'Refusing to overwrite {output}')
        original = inspect(source)
        print(f'Creating Video {number} at {rate:g}x with pitch-preserving audio.', flush=True)
        subprocess.run([
            FFMPEG, '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
            '-i', str(source), '-filter_complex',
            f'[0:v]setpts=(PTS-STARTPTS)/{rate}[v];'
            f'[0:a]asetpts=PTS-STARTPTS,atempo={rate}[a]',
            '-map', '[v]', '-map', '[a]', '-c:v', 'libx264',
            '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(output)
        ], check=True)
        final = inspect(output)
        duration = float(final['format']['duration'])
        expected = float(original['format']['duration']) / rate
        if duration >= limit or abs(duration-expected) > 0.6:
            raise RuntimeError(f'Unexpected duration {duration:.3f}s for Video {number}')
        if not {'video', 'audio'}.issubset({s['codec_type'] for s in final['streams']}):
            raise RuntimeError('Missing video or audio stream')
        # Decode the whole exported file to detect damaged video/audio packets.
        subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-xerror',
                        '-i', str(output), '-f', 'null', '-'], check=True)
        print(f'Verified {output.name}: {duration:.2f}s; audio/video decode passed.', flush=True)
    print('Video 3 unchanged. Full-length originals unchanged.', flush=True)


if __name__ == '__main__':
    main()
