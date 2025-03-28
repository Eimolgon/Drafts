import numpy as np
import random
import datetime

def check_duplicate(samp: list) -> bool:
    '''
    Check if any number is duplicated inside the list.
    '''
    for i in samp:
        if samp.count(i) > 1:
            return True
        else:
            return False

n_videos = 100
n_participants = 20
amount = 15

# ----- ----- -----
# This is only for short tests
# n_videos = 50
# n_participants = 5
# amount = 3
# ----- ----- -----

videos = np.arange(1, n_videos+1)
participants = np.arange(1, n_participants+1)

sorteo = {}

for i in participants:
    rand_list = random.sample(range(1, n_videos+1), amount)
    if check_duplicate(rand_list):
        rand_list = random.sample(range(1, n_videos), amount)
    
    rand_list.sort()
    sorteo[i] = rand_list


file = open('forms/sorteo-result.txt', 'w')

file.write('Date: {0}'.format(datetime.datetime.now()) + '\n')

for j in range(1, len(sorteo)+1):
    file.write('Participant {0}: '.format(j) + str(sorteo[j]) + '\n')
    # print('Participant {0}: '.format(j) + str(sorteo[j]) + '\n')

for k in range(1, n_participants+1):
    file2 = open(f'forms/class-form-{k}.txt', 'w')
    file2.write('Participant {}'.format(k) + '\n')
    file2.write('============== \n \n')

    for ik in range(len(sorteo[k])):
        # print('Video {0}:'.format(sorteo[k][ik]) + '\n')
        file2.write('Video {0}:'.format(sorteo[k][ik]) + '\n')
