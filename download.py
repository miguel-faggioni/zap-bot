#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download videos from a list of subreddits.

Usage example:
  $ python download.py

"""

import unittest
import random
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.common.by import By

## global variables
baseUrl = 'https://old.reddit.com/'
subreddits = [
    # fails
    'nonoyesyesnonononono',
    'yesyesyesyesno',
    'yesyesyesno',
    # wtf
    'nonononowaitwhat',
    'maybemaybemaybe',
    'woahdude',
    # wins
    'nonononoyes',
    'yesyesyesdamn'
]
profilePath = '/home/miguel/.mozilla/firefox/y559xu9q.selenium'


class DownloadFromReddit(unittest.TestCase):

    # open the browser and configure it to
    # close after everything ran
    def setUp(self):
        self.browser = webdriver.Firefox(profilePath)
        self.addCleanup(self.browser.quit)
        
    # open the subreddit and get the first post
    # that hasn't been downloaded yet
    def testGetPost(self):
        # open subreddit
        subreddit = random.choice(subreddits)
        self.browser.get('{}r/{}'.format(baseUrl,subreddit))
        # get 1st post
        WebDriverWait(self.browser, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, 'a.expando-button.collapsed.video'))
        post = self.browser.find_element(By.CSS_SELECTOR, 'a.expando-button.collapsed.video')
        # open the video
        post.click()
        # get source
        WebDriverWait(self.browser, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, 'a.res-video-link.res-video-source'))
        source = self.browser.find_element(By.CSS_SELECTOR, 'a.res-video-link.res-video-source').get_attribute('href')
        print(source)
        
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
