#!/usr/bin/env python3

import ssl
import json
import time
import schedule
import shutil
from datetime import datetime
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

        if iPost.author == post.author and abs((iPost.createdDate - post.createdDate).total_seconds()) < 300:
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

def moveOldPosts():
    files = os.listdir('./_posts')
    files.sort(reverse=True)

    for filename in files:
        if fileDates(filename) > 15:
            print('Move:', filename)
            source = os.path.join('./_posts', filename)
            dest = os.path.join('./_drafts', filename)
            shutil.move(source, dest)









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


dailyPosts = 0
crawlerTime = 0

def scheduleCrawler():
    global dailyPosts
    global crawlerTime

    try:
        moveOldPosts()

        crawler = crawlerPages()
        posts = crawler[0]
        crawlerReport = crawler[1]

        if len(posts) > 0:
            createMarkdownFile(posts)
            # savePostsInfor(posts)
        
        pushToGithub()

        dailyPosts = dailyPosts + len(posts)
        crawlerTime = crawlerTime + 1

        if crawlerTime % 12 == 0:
            now = datetime.now()
            subject = '[Ps] ' + str(dailyPosts) + ' posts on ' + now.strftime("%d/%m")
            crawlerReport = crawlerReport + '\n\n' + 'Last crawler ' + str(len(posts)) + ' posts.'
            report.sendReportEmail(subject, crawlerReport)
    
    except Exception as e:
        now = datetime.now()
        subject = '[Ps] ERROR ... (' + now.strftime("%Hh%M %d/%m") + ')'
        message = 'Ps error: ' + str(e)
        report.sendReportEmail(subject, message)
    
    # finally:
    #     now = datetime.now()
    #     subject = '[Ps] FINISHED! (' + now.strftime("%Hh%M %d/%m") + ')'
    #     report.sendReportEmail(subject, '')
    










# schedule.every().day.at("15:10").do(scheduleCrawler, 'It it 15:10')
# schedule.every(2).hours.do(scheduleCrawler)
# schedule.every(5).minutes.do(scheduleCrawler)





schedule.every(2).hours.do(scheduleCrawler)
while True:
    schedule.run_pending()
    time.sleep(60)










# scheduleCrawler()

# crawlerSubreddit()

# moveOldPosts()
