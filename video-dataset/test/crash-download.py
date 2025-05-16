import yt_dlp
from yt_dlp.utils import download_range_func
import csv

'''
The dataset should be in .csv format, the columns are Index, URL, Start time,
End time.

Cookies file is in Netscape HTTP format.
'''

#file = '/mnt/c/Users/begtgonzalez/Onedrive - Delft University of Technology/Documents/University/Data/dataset-yt4.csv'
file = '/mnt/c/Users/begtgonzalez/Onedrive - Delft University of Technology/Documents/University/Bicycle-Crashes/Data/02-Video-labelling/dataset-nocrash.csv'
cookie_path = '/mnt/c/Users/begtgonzalez/Onedrive - Delft University of Technology/Documents/University/Data/Cookies2.txt'


with open(file, newline = '') as csvfile:
    readFile = csv.reader(csvfile)
    # This is to skip the first line of the .csv that contains the titles.
    next(readFile, None)
    for lines in readFile:
        idx = lines[0]
        url = lines[1]
        start_time = int(lines[2])
        end_time = int(lines[3])
        
        # Use try except to not feed the cookies unless is extrictly necessary.
        try:
            yt_opts = {
                'verbose': True,
                'outtmpl': f'/mnt/c/Users/begtgonzalez/Onedrive - Delft University of Technology/Documents/University/Bicycle-Crashes/Video/Dataset-NoCrash/yt-nocrash-{idx}',
                'download_ranges': download_range_func(None, [(start_time, end_time)]),
                'force_keyframes_at_cuts': True,
                'format_sort': ['res:1080', 'ext:mp4:m4a'],
                }
            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                ydl.download(url)

        except:
            yt_opts = {
                'verbose': True,
                'outtmpl': f'/mnt/c/Users/begtgonzalez/Onedrive - Delft University of Technology/Documents/University/Bicycle-Crashes/Video/Dataset/{idx}',
                'download_ranges': download_range_func(None, [(start_time, end_time)]),
                'force_keyframes_at_cuts': True,
                'format_sort': ['res:1080', 'ext:mp4:m4a'],
                'cookiefile': cookie_path,
                }
            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                ydl.download(url)
