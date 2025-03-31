import csv

def detect_format(given_time):
    
    time_list = list(given_time)

    if ':' in time_list:
        divisions = time_list.count(':')

        if divisions == 1:
            # min * 60 + sec
        elif divisions == 2:
            # hrs * 3600 + min * 60 + sec


while True:

    n_videos = int(input('How many videos do you want to add?: '))

    for i in range(n_videos):
        url = str(input('Input video URL (if it is the same than before just 
            press enter): '))
        start = input('Specify starting time of the video: ')
        finish = input('Specify ending time of the video: ')

