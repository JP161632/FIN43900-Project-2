"""Combine local screen/camera pairs without putting recordings in the repository.

Requires an explicit output folder. Original recordings are never modified.
Run only for the student-authorized local media task; no upload is performed.
"""
import argparse
import json
import os
import subprocess
from pathlib import Path

PAIRS = [
    (1, 'E23925E5-1A32-49E6-8A14-BC8D474EDC66-.mp4',
     'B0C719CA-D90B-4605-9622-B04AB044699B-.mp4'),
    (2, '691F1B11-7030-4FE3-B34F-08D7E9013DC0-.mp4',
     '87AE22EB-3C52-457A-AB50-506FDD1B4A17-.mp4'),
    (3, 'A8575C52-6161-4189-983D-16899F178A2F-.mp4',
     'B3EF880A-83B4-4D39-8EF2-AE029321C477-.mp4'),
]
FFMPEG = r'C:\ffmpeg\bin\ffmpeg.exe'
FFPROBE = r'C:\ffmpeg\bin\ffprobe.exe'


def probe(path):
    return json.loads(subprocess.check_output([
        FFPROBE, '-v', 'error', '-show_entries',
        'stream=codec_type,width,height:format=duration', '-of', 'json', str(path)
    ], text=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(os.environ['LOCALAPPDATA'])/'Kaltura'/'Capture'/'Recordings'
    prepared = []
    for number, screen_name, camera_name in PAIRS:
        paths = []
        for name in [screen_name, camera_name]:
            found = list(root.rglob(name))
            if len(found) != 1:
                raise RuntimeError(f'Expected one source for {name}, found {len(found)}')
            paths.append(found[0])
        screen, camera = paths
        s, c = probe(screen), probe(camera)
        if abs(float(s['format']['duration'])-float(c['format']['duration'])) > 1:
            raise RuntimeError(f'Video {number}: source durations do not align')
        if not any(stream['codec_type'] == 'audio' for stream in s['streams']):
            raise RuntimeError(f'Video {number}: screen source has no audio stream')
        target = args.output/f'Project-2-Video-{number}-Combined-Full-Length.mp4'
        if target.exists():
            raise FileExistsError(f'Output already exists; refusing to overwrite: {target}')
        prepared.append((number, screen, camera, target, float(s['format']['duration'])))
    args.output.mkdir(parents=True, exist_ok=True)
    for number, screen, camera, target, expected_duration in prepared:
        print(f'Combining Video {number}; originals remain unchanged.', flush=True)
        subprocess.run([
            FFMPEG, '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
            '-i', str(screen), '-i', str(camera),
            '-filter_complex',
            '[0:v]setpts=PTS-STARTPTS[screen];'
            '[1:v]setpts=PTS-STARTPTS,scale=320:180,setsar=1,'
            'pad=328:188:4:4:color=white[camera];'
            '[screen][camera]overlay=W-w-24:H-h-24:eof_action=repeat:repeatlast=1[v]',
            '-map', '[v]', '-map', '0:a:0',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
            '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', str(target)
        ], check=True)
        output = probe(target)
        duration = float(output['format']['duration'])
        if abs(duration-expected_duration) > 0.5:
            raise RuntimeError(f'Video {number}: unexpected output duration {duration}')
        if not any(stream['codec_type'] == 'audio' for stream in output['streams']):
            raise RuntimeError(f'Video {number}: output audio missing')
        print(f'Created {target.name}: {duration:.2f}s; video and audio present.', flush=True)
    print(f'Finished. Review videos in: {args.output}', flush=True)
    print('Full-length copies: trim Video 1 to <=3:00 and Video 2 to <=5:00 before submission.', flush=True)


if __name__ == '__main__':
    main()
