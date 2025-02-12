import yt_dlp
from yt_dlp.utils import download_range_func
import csv

file = '/mnt/c/Users/begtgonzalez/Onedrive - Delft University of Technology/Documents/University/Data/dataset-yt3.csv'



with open(file, newline = '') as csvfile:
    readFile = csv.reader(csvfile)
    next(readFile, None)
    for lines in readFile:
        idx = lines[0]
        url = lines[1]
        start_time = int(lines[2])
        end_time = int(lines[3])
        crash_type = lines[4]

        try:
            yt_opts = {
                'verbose': True,
                'outtmpl': f'/mnt/c/Users/begtgonzalez/Onedrive - Delft University of Technology/Documents/University/Bicycle-Crashes/Video/yt-crash-{idx}-{crash_type}',
                'download_ranges': download_range_func(None, [(start_time, end_time)]),
                'force_keyframes_at_cuts': True,
                'format_sort': ['res:1080', 'ext:mp4:m4a'],
                }
            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                ydl.download(url)

        except:
            cookie_path = '/mnt/c/Users/begtgonzalez/Onedrive - Delft University of Technology/Documents/University/Data/Cookies.txt'
            yt_opts = {
                'verbose': True,
                'outtmpl': f'/mnt/c/Users/begtgonzalez/Onedrive - Delft University of Technology/Documents/University/Bicycle-Crashes/Video/yt-crash-{idx}-{crash_type}',
                'download_ranges': download_range_func(None, [(start_time, end_time)]),
                'force_keyframes_at_cuts': True,
                'format_sort': ['res:1080', 'ext:mp4:m4a'],
                'cookiefile': cookie_path,
                }
            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                ydl.download(url)