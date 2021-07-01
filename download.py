#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download videos from a list of subreddits.

Usage example:
  $ python download.py

"""

import random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import youtube_dl
import shutil
import os

DOWNLOAD_ARCHIVE_FILE = 'videos/download.archive'
PROFILE_PATH = '/home/miguel/.mozilla/firefox/y559xu9q.selenium'

# highlight a given element for debugging
def highlight(element):
    """Highlights (blinks) a Selenium Webdriver element"""
    driver = element._parent

    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)
    original_style = element.get_attribute('style')
    apply_style("background: yellow; border: 2px solid red;")
    time.sleep(.3)
    apply_style(original_style)


class DownloadFromReddit:
    def __init__(self):
        self.baseUrl = 'https://old.reddit.com/'
        self.subreddits = [
            # fails
            'nonoyesyesnonononono',
            'yesyesyesyesno',
            'yesyesyesno',
            'nononono',
            # wtf
            'nonononowaitwhat',
            'maybemaybemaybe',
            'unexpected',
            # wins
            'woahdude',
            'nonononoyes',
            'yesyesyesdamn'
        ]
        self.profilePath = PROFILE_PATH

    # open the browser
    def setUp(self):
        options = Options()
        #options.headless = True
        self.browser = webdriver.Firefox(self.profilePath, options=options)

    # close browser
    def cleanUp(self):
        self.browser.close()
        self.browser.quit()

    # disable the style of the subreddit
    def disableSubStyle(self):
        id = 'res-style-checkbox'
        WebDriverWait(self.browser, 10).until(lambda x: x.find_element(By.ID, id))
        self.browser.find_element(By.ID, id).click()

    # get the url for a given subreddit, or for a random one
    def getSubredditUrl(self, subreddit=None):
        if subreddit is None:
            subreddit = random.choice(self.subreddits)
        return '{}r/{}'.format(self.baseUrl, subreddit)

    # get all video posts on the page
    def getVideoPosts(self):
        css = 'a.expando-button.collapsed.video'
        try:
            WebDriverWait(self.browser, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, css))
            buttons = self.browser.find_elements(By.CSS_SELECTOR, css)
            return [button.find_element(By.XPATH, './../..') for button in buttons]
        except Exception as e:
            return []

    # get the element of the expando button of a post
    def getExpandoButton(self, post):
        css = 'a.expando-button.collapsed.video'
        WebDriverWait(post, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, css))
        return post.find_element(By.CSS_SELECTOR, css)
    
    # get the origin of a post
    def getPostOrigin(self, post):
        css = 'p.title > span.domain > a'
        WebDriverWait(post, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, css))
        return post.find_element(By.CSS_SELECTOR, css).text

    # get the url source of a video post
    def getVideoSource(self, post):
        origin = self.getPostOrigin(post)
        if 'youtube' in origin.replace('.', ''):
            css = 'iframe'
            attribute = 'src'
        else:
            css = 'a.res-video-link.res-video-source'
            attribute = 'href'
        WebDriverWait(post, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, css))
        return post.find_element(By.CSS_SELECTOR, css).get_attribute(attribute)

    # get the title of a post
    def getPostTitle(self, post):
        css = 'p.title > a.title'
        WebDriverWait(post, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, css))
        return post.find_element(By.CSS_SELECTOR, css).text

    # go to the next page
    def nextPage(self):
        css = 'span.next-button'
        self.browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        WebDriverWait(self.browser, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, css))
        self.browser.find_element(By.CSS_SELECTOR, css).click()

    # download a video and saves it to `videos/<name>.mp4`
    def download(self, url, name, skipExisting=False):
        # check if file already exists
        destination = '{}/videos/{}.mp4'.format(os.getcwd(), name)
        if os.path.isfile(destination):
            print(' > File already exists, not downloading it again')
            downloadFile = False
        else:
            downloadFile = True
        # return early 
        if downloadFile is False and skipExisting is True:
            return None
        # download options
        ydl_opts = {
            # https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312
            'outtmpl': 'video.mp4',
            'format': 'mp4',
            'nooverwrites': True,
            'quiet': True,
            'download_archive': '{}/{}'.format(os.getcwd(), DOWNLOAD_ARCHIVE_FILE)
        }
        # download the file
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(
                    url,
                    download=downloadFile
                )
            video = result
        except Exception as e:
            print(e)
            return None
        # move file to `videos/`
        source = '{}/{}'.format(os.getcwd(), 'video.mp4')
        if downloadFile and os.path.isfile(source):
            shutil.move(source, destination)
        # return the video
        return video

    def downloadVideos(self, subreddit=None, howMany=20, skipExisting=False):
        # if no subreddit was received, choose a random one
        if subreddit is None:
            subreddit = random.choice(self.subreddits)

        # go to subreddit
        print(' ----> Going on r/{}'.format(subreddit))
        self.browser.get(self.getSubredditUrl(subreddit))

        # disable the custom stlyle
        self.disableSubStyle()

        # while the quota isn't met
        videosDownloaded = []
        while len(videosDownloaded) < howMany:
            # get all video posts on the page
            posts = self.getVideoPosts()
            print(' ----> Found {} videos'.format(len(posts)))
            for index, post in enumerate(posts):
                print('')
                print(' --> Post {}:'.format(index + 1))
                try:
                    # expand the video
                    button = self.getExpandoButton(post)
                    button.click()
                    # get its title
                    title = self.getPostTitle(post)
                    print(' --> {}'.format(title))
                    # get the source url
                    url = self.getVideoSource(post)
                    print(' --> {}'.format(url))
                    # download the video
                    downloadedVideo = self.download(url, title, skipExisting=skipExisting)
                    if downloadedVideo is not None:
                        videosDownloaded.append(downloadedVideo)
                    print(' > {}/{} videos downloaded'.format(len(videosDownloaded), howMany))
                    # collapse the video
                    button.click()
                except Exception as e:
                    print(' > FAIL'.format(title))
                    print(e)

            # if the quota was met
            if len(videosDownloaded) < howMany:
                return videosDownloaded
            
            # go to next page and repeat until the quota is met
            print(' ----> Going to next page')
            self.nextPage()

        

if __name__ == '__main__':
    # setup
    bot = DownloadFromReddit()
    bot.setUp()

    # download videos
    bot.downloadVideos(howMany=5,skipExisting=True)

    # close browser
    bot.cleanUp()
