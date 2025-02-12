import csv

file = '/home/eimolgon/Documents/University/Other/dataset-yt2.csv'


with open(file, newline = '') as csvfile:
    readFile = csv.reader(csvfile)
    next(readFile, None)
    for lines in readFile:
        idx = lines[0]
        url = lines[1]
        start = int(lines[2])
        end = int(lines[3])
        crash_type = lines[4]
        
        print('Index: {idx}, Duration: {time_window}, Type: {crashClass}'.format(idx = idx, time_window = end-start, crashClass = crash_type))
