#!/usr/bin/env python3

import ssl
import json
import time
import schedule
import shutil
import zipfile
from datetime import datetime, timedelta
from datetime import date

import os
import os.path
from os import path

from pages import report
from pages.reddit import SubReddit
from pages.reddit import Post

ssl._create_default_https_context = ssl._create_unverified_context

def crawlerSubreddit():
    with open('subreddit.json') as file:
        data = json.load(file)
    
    subreddit = SubReddit(json.dumps(data))
    print('Subreddit:', subreddit.name)
    crawlerPosts = subreddit.loadPosts()

    if len(crawlerPosts) == 0:
        return

    crawlerFilename = subreddit.displayName + datetime.now().strftime("_%Y-%m-%d-%H%M%S") + '.json'
    postsFilename = subreddit.displayName + '-posts' + datetime.now().strftime("_%Y-%m-%d-%H%M%S") + '.json'

    savePosts(crawlerPosts, crawlerFilename)

    posts = removeDuplicatePosts(crawlerPosts)

    savePosts(posts, postsFilename)

    createMarkdownFile(posts)

def isDuplicatePost(posts, post):
    for iPost in posts:
        if iPost.sourceUrl == post.sourceUrl:
            return True

        # if iPost.author == post.author and abs((iPost.createdDate - post.createdDate).total_seconds()) < 300:
        if iPost.postId == post.postId:
            print('Same author post')
            return True

    return False

def removeDuplicatePosts(posts):    
    news = []
    for post in posts:
        if isDuplicatePost(news, post) == False:
            news.append(post)
    
    return news

def loadPosts(filename):
    with open(filename) as file:
        data = json.load(file)
    
    posts = []
    for dict in data['posts']:
        post = Post(json.dumps(dict))
        posts.append(post)

    return posts

def savePosts(posts, filename):
    directory = './posts-crawler/'
    if not os.path.isdir(directory):
        os.mkdir(directory)

    filepath = os.path.join(directory, filename)

    postData = {}
    postData["posts"] = []
    for new in posts:
        postData["posts"].append(new.__dict__)
    
    with open(filepath, 'w', encoding="utf8") as postFile:
        json.dump(postData, postFile, ensure_ascii=False, indent=4)





def fileDates(fileName):
    names = fileName.split('-')
    if len(names) > 0:
        dateStrings = names[-1].split('.')
        if len(dateStrings) > 0:
            dateString = dateStrings[0]
            if len(dateString) > 0:
                fileDate = datetime.strptime(dateString, '%Y%m%d%H%M%S%f')

                today = datetime.now()
                days = (today - fileDate).days
                return days
    
    return -1

def backupPosts():
    files = os.listdir('./_posts')
    files.sort(reverse=True)

    yesterday = datetime.now() - timedelta(days=1)
    folderName = yesterday.strftime('%Y-%m-%d')
    
    # Zip posts
    backupFile = folderName + '.zip'
    zf = zipfile.ZipFile(os.path.join('./_drafts', backupFile), "w")
    for file in files:
        zf.write(os.path.join('./_posts', file))
    zf.close()

    # Move posts
    backupFolder = os.path.join('./_posts', folderName)
    os.mkdir(backupFolder)

    for filename in files:
        source = os.path.join('./_posts', filename)
        shutil.move(source, backupFolder)
    
    # for file in files:
    #     os.remove(os.path.join('./_posts', file))





def filepath():
    directory = './posts-data/'
    if not os.path.isdir(directory):
        os.mkdir(directory)

    filename = 'posts' + datetime.now().strftime("_%Y-%m-%d-%H%M%S") + ".json"
    filepath = os.path.join(directory, filename)
    return filepath


def savePostsInfor(posts):
    postData = {}
    postData["posts"] = []
    for new in posts:
        postData["posts"].append(new.__dict__)
    
    with open(filepath(), 'w', encoding="utf8") as postFile:
        json.dump(postData, postFile, ensure_ascii=False, indent=4)


def createMarkdownFile(posts):
    if len(posts) > 0:
        for post in posts:
            try:
                post.createMarkdownFile()

            except Exception as e:
                now = datetime.now()
                subject = '[Ps] Post error (' + now.strftime("%Hh%M %d/%m") + ')'
                message = 'Ps error: ' + str(e) + '\nPost:\n' + post.markdownText()
                report.sendReportEmail(subject, message)
            

def pushToGithub():
    print('pushToGithub')
    # gitStatus = os.system('git status')
    
    message = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gitAdd = 'git add .'
    gitCommit = 'git commit -m ' + '\"' + message + '\"'
    gitPush = 'git push -u origin master'
    os.system(gitAdd)
    os.system(gitCommit)
    os.system(gitPush)


def crawlerPages():
    with open('subreddits.json') as pagesFile:
        data = json.load(pagesFile)

    news = []
    report = ''
    for dict in data['subreddits']:
        subreddit = SubReddit(json.dumps(dict))
        posts = subreddit.loadPosts()

        report = report + '\n\n' + '[' + str(len(posts)) + ']: ' + subreddit.name

        for post in posts:
            news.append(post)
    
    return [news, report]



def postsCrawler():

    try:
        dailyPosts = 0

        crawler = crawlerPages()
        posts = crawler[0]
        crawlerReport = crawler[1]

        if len(posts) > 0:
            backupPosts()
            createMarkdownFile(posts)
        
        pushToGithub()

        print(crawlerReport)

        dailyPosts = dailyPosts + len(posts)
        
        now = datetime.now()
        subject = '[Ps] ' + str(dailyPosts) + ' posts on ' + now.strftime("%d/%m")
        crawlerReport = crawlerReport + '\n\n' + 'Last crawler ' + str(len(posts)) + ' posts.'
        report.sendReportEmail(subject, crawlerReport)
    
    except Exception as e:
        now = datetime.now()
        subject = '[Ps] ERROR ... (' + now.strftime("%Hh%M %d/%m") + ')'
        message = 'Ps error: ' + str(e)
        report.sendReportEmail(subject, message)
    


def scheduleCrawler():
    schedule.every().day.at("00:05").do(postsCrawler)
    while True:
        schedule.run_pending()
        time.sleep(60)








# scheduleCrawler()

# crawlerSubreddit()

# moveOldPosts()


postsCrawler()

# backupPosts()