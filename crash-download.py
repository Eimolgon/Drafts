import yt_dlp
from yt_dlp.utils import download_range_func


start_time = 158
end_time = 160

idx = 1

cookie_path = '/mnt/c/Users/begtgonzalez/Onedrive - Delft University of Technology/Documents/University/Data/Cookies.txt'

yt_opts = {
    'verbose': True,
    'outtmpl': f'/mnt/c/Users/begtgonzalez/Onedrive - Delft University of Technology/Documents/University/Bicycle-Crashes/Video/yt-crash-{idx}',
    'download_ranges': download_range_func(None, [(start_time, end_time)]),
    'force_keyframes_at_cuts': True,
    'format_sort': ['res:1080', 'ext:mp4:m4a'],
    'cookiefile': cookie_path,
    }


url = 'https://www.youtube.com/watch?v=pCtAgvrcOHs'

with yt_dlp.YoutubeDL(yt_opts) as ydl:
    ydl.download(url)
