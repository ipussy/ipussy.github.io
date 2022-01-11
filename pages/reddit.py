#!/usr/bin/env python3

import json
import time
import urllib.request
import requests
import bs4
from bs4 import BeautifulSoup
from datetime import datetime
import os.path
from os import path

class Image(object):
    url = ''
    width = ''
    height = ''

    def __init__(self, data):
        self.__dict__ = json.loads(data)

    def link(self):
        return self.url.replace("amp;", "")











class Post(object):
    imageId = ''
    postId = ''
    title = ''
    summary = ''
    subReddit = ''
    createdTime = 0.0

    author = ''
    # authorFullname = ''
    
    # sourceImage: Image
    # resolutionImage = []
    
    sourceUrl = ''
    sourceWidth = 0
    sourceHeight = 0

    thumbUrl = ''
    thumbWidth = 0
    thumbHeight = 0
    

    def __init__(self, data):
        self.__dict__ = json.loads(data)

    def sourceLink(self):
        return self.sourceUrl.replace("amp;", "")
    
    def thumbLink(self):
        return self.thumbUrl.replace("amp;", "")
    
    def filename(self):
        name = datetime.fromtimestamp(self.createdTime).strftime("%Y-%m-%d-")
        # name = datetime.now().strftime("%Y-%m-%d-")
        time = datetime.now().strftime("%Y%m%d%H%M%S%f")
        for character in self.title:
            if character.isalnum() or character == ' ':
                name += character

        encodedString = name.encode("ascii", "ignore")
        decodeString = encodedString.decode()

        filename = decodeString.strip().replace(" ", "-")
        if len(filename) > 225:
            filename = filename[:225]

        return filename.strip().replace(" ", "-") + "-" + time + ".md"

    def createdDate(self):
        return datetime.fromtimestamp(self.createdTime)
    
    def logInfo(self):
        print('\n- Title:', self.title)
        print('- Link :', self.sourceLink())
        print('- Summary:', self.summary)
    
    def markdownText(self):
        # print('Filename:', self.filename())
        text = """---
title:  "{title}"
metadate: "hide"
categories: [ {subreddit} ]
image: "{image}"
thumb: "{thumb}"
visit: ""
---
{content}
"""

        text = text.replace("{title}", self.title.replace("\"", ""))
        text = text.replace("{image}", self.sourceLink())
        text = text.replace("{thumb}", self.thumbLink())
        text = text.replace("{subreddit}", self.subReddit)
        text = text.replace("{content}", self.summary)

        return text
    
    def createMarkdownFile(self):
        directory = './_posts/'
        if not os.path.isdir(directory):
            os.mkdir(directory)

        filename = self.filename()
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding="utf8") as postFile:
            postFile.write(self.markdownText())










# http://www.reddit.com/r/GodPussy/new.json?limit=100&show=all
class SubReddit(object):
    name = ''
    displayName = ''
    summary = ''
    thumbLink = ''
    afterKey = ''

    def __init__(self, data):
        self.__dict__ = json.loads(data)
    
    def requestLink(self):
        if not self.afterKey:
            return 'http://www.reddit.com/r/' + self.displayName + '/new.json?limit=100&show=all'
        else:
            return 'http://www.reddit.com/r/' + self.displayName + '/new.json?limit=100&after=' + self.afterKey

    def loadPosts(self):
        posts = []
        
        # backupPostId = self.backupPostId()
        timeStamp = self.timeStamp()
        if timeStamp != None:
            timeStr = datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S")
            print('[', self.name, '] latest post at:', timeStr)
        else:
            print('[', self.name, '] posts.')
        loopCount = 0
        isBackupId = False

        while True:

            jsonResponse = requests.get(self.requestLink(), headers = {'User-agent': 'Pussy.'})
            output = jsonResponse.json()

            kind = output['kind']
            if kind == 'Listing':
                data = output['data']

                self.afterKey = data['after']

                hasBackupPost = False
                for dict in data['children']:
                    post = self.post(dict)
                    if post != None:
                        # print('[', post.postId, ']')

                        if isBackupId == False:
                            isBackupId = True
                            self.backupPost(post)
                        
                        # if backupPostId != None and post.postId == backupPostId:
                        if timeStamp != None and post.createdTime <= timeStamp:
                            hasBackupPost = True

                            # if len(posts) > 0:
                                # self.savePosts(posts)
                            print('\tFinished (time stamp)')
                            break

                        posts.append(post)
                
                print('\tPosts [' + str(loopCount + 1) + ']: ' + str(len(posts)))
                if hasBackupPost == True:
                    print('\t\tMeet backup post!')
                    break
                
            loopCount = loopCount + 1

            if loopCount == 100:
                # self.savePosts(posts)
                print('\tFinished.')
                break
            # return posts

        return posts

    # def filepath(self):
    #     directory = './posts-data/'
    #     if not os.path.isdir(directory):
    #         os.mkdir(directory)

    #     filename = self.displayName + datetime.now().strftime("_%Y-%m-%d-%H%M%S") + ".json"
    #     filepath = os.path.join(directory, filename)
    #     return filepath

    # def savePosts(self, posts):
    #     postData = {}
    #     postData["posts"] = []
    #     for new in posts:
    #         postData["posts"].append(new.__dict__)
        
    #     with open(self.filepath(), 'w', encoding="utf8") as postFile:
    #         json.dump(postData, postFile, ensure_ascii=False, indent=4)

    def backupPost(self, post):
        postDict = {}
        postDict['subreddit'] = self.displayName
        postDict['imageId'] = post.imageId
        postDict['postId'] = post.postId
        postDict['timeStamp'] = post.createdTime

        if path.exists('backup.json') == True:
            with open("backup.json") as backupFile:
                data = json.load(backupFile)

            dict = data['subreddits']

            hasSubReddit = False
            for subDict in dict:
                if subDict['subreddit'] == self.displayName:
                    hasSubReddit = True
                    # subDict['postId'] = post.postId
                    subDict['timeStamp'] = post.createdTime
            
            if hasSubReddit == False:
                dict.append(postDict)
            with open("backup.json", 'w') as backupFile:
                json.dump(data, backupFile)
        else:
            dict = {}
            dict['subreddits'] = []
            dict['subreddits'].append(postDict)
            with open("backup.json", 'w') as backupFile:
                json.dump(dict, backupFile)
    
    def backupPostId(self):
        if path.exists('backup.json') == True:
            with open("backup.json") as backupFile:
                data = json.load(backupFile)

            dict = data['subreddits']

            for subDict in dict:
                if subDict['subreddit'] == self.displayName:
                    return subDict['postId']
        return None

    def timeStamp(self):
        if path.exists('backup.json') == True:
            with open("backup.json") as backupFile:
                data = json.load(backupFile)

            dict = data['subreddits']

            for subDict in dict:
                if subDict['subreddit'] == self.displayName:
                    return subDict['timeStamp']
        return None
    
    def post(self, dict):
        kind = dict['kind']
        if kind == 't3':
            if not 'data' in dict:
                return None
            data = dict['data']

            if not 'id' in data:
                return None
            postId = data['id']

            if not 'title' in data:
                return None
            title = data['title']

            summary = ''
            if 'link_flair_text' in data:
                summary = data['link_flair_text']
            
            if not summary:
                summary = title

            if not 'preview' in data:
                return None

            if not 'created_utc' in data:
                return None
            createdTime = data['created_utc']
            
            author = data['author']
            # authorFullname = data['author_fullname']

            previewDict = data['preview']

            imageId = previewDict['images'][0]['id']
            sourceImage = previewDict['images'][0]['source']
            thumbImage = previewDict['images'][0]['resolutions'][-1]
            url = sourceImage['url']
            width = sourceImage['width']
            height = sourceImage['height']

            thumbUrl = thumbImage['url']
            thumbWidth = thumbImage['width']
            thumbHeight = thumbImage['height']
            
            itemDict = {}
            itemDict['postId'] = postId
            itemDict['imageId'] = imageId
            itemDict['subReddit'] = self.name
            itemDict['title'] = title
            itemDict['summary'] = summary
            itemDict['createdTime'] = createdTime

            itemDict['sourceUrl'] = url
            itemDict['sourceWidth'] = width
            itemDict['sourceHeight'] = height

            itemDict['thumbUrl'] = thumbUrl
            itemDict['thumbWidth'] = thumbWidth
            itemDict['thumbHeight'] = thumbHeight

            itemDict['author'] = author
            # itemDict['authorFullname'] = authorFullname

            # print('Title:', title, '\nLink:', url, '\nSummary:', summary)
    
            return Post(json.dumps(itemDict))
        
        return None

        

    
