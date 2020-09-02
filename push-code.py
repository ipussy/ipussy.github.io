#!/usr/bin/env python3

import os
import os.path
from os import path
from datetime import datetime


def pushToGithub():
    print('pushToGithub')
    gitStatus = os.system('git status')
    
    print('Status', gitStatus)

    message = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gitAdd = 'git add .'
    gitCommit = 'git commit -m ' + '\"' + message + '\"'
    gitPush = 'git push -u origin master'
    os.system(gitAdd)
    os.system(gitCommit)
    os.system(gitPush)

pushToGithub()


