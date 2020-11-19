#!/usr/bin/env python3

import os
import os.path
import time
from datetime import datetime
from datetime import date
import shutil


def fileDates(fileName):
    names = fileName.split('-')
    if len(names) > 0:
        dateStrings = names[-1].split('.')
        if len(dateStrings) > 0:
            dateString = dateStrings[0]
            fileDate = datetime.strptime(dateString, '%Y%m%d%H%M%S%f')

            today = datetime.now()
            days = (today - fileDate).days
            print(days)
            return days
    
    return -1

def moveOldPosts():
    files = os.listdir('./_posts')
    files.sort(reverse=True)

    for file in files:
        print(file)

    for filename in files:
        if fileDates(filename) > 15:
            shutil.move('./_posts/' + filename, './_drafts/' + filename)
        else:
            break

moveOldPosts()