import yt_dlp
from yt_dlp.utils import download_range_func

url = str(input('Paste your URL here: '))
start_time = int(input('Paste yout start time (in seconds): '))
end_time = int(input('Paste yout end time (in seconds): '))
NAME = str(input('Input file name: '))


yt_opts = {
        'verbose': True,
        'outtmpl': f'{NAME}',
        'download_ranges': download_range_func(None, [(start_time,
                                                       end_time)]),
        'force_keyframes_at_cuts': True,
        'format_sort': ['res:1080', 'ext:mp4:m4a'],
        }

with yt_dlp.YoutubeDL(yt_opts) as ydl:
    ydl.download(url)

