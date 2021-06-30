#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download videos from a list of subreddits.

Usage example:
  $ python download.py

"""

import random
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.common.by import By
import time

# highlight a given element for debugging
def highlight(element):
    """Highlights (blinks) a Selenium Webdriver element"""
    driver = element._parent
    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",element, s)
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
            # wtf
            'nonononowaitwhat',
            'maybemaybemaybe',
            'unexpected',
            # wins
            'woahdude',
            'nonononoyes',
            'yesyesyesdamn'
        ]
        self.profilePath = '/home/miguel/.mozilla/firefox/y559xu9q.selenium'
        
    # open the browser
    def setUp(self):
        self.browser = webdriver.Firefox(self.profilePath)

    # close browser
    def cleanUp(self):
        self.browser.quit()

    # disable the style of the subreddit
    def disableSubStyle(self):
        self.browser.find_element(By.ID, 'res-style-checkbox').click()

    # get the url for a given subreddit, or for a random one
    def getSubredditUrl(self, subreddit = None):
        if subreddit == None:
            subreddit = random.choice(self.subreddits)
        return '{}r/{}'.format(self.baseUrl,subreddit)

    # get all video posts on the page
    def getVideoPosts(self):
        css = 'a.expando-button.collapsed.video'
        try:
            WebDriverWait(self.browser, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, css))
            buttons = self.browser.find_elements(By.CSS_SELECTOR, css)
            return [ button.find_element(By.XPATH, "./../..") for button in buttons ]
        except Exception as e:
            return []
        

        
if __name__ == '__main__':
    b = DownloadFromReddit()
    b.setUp()
    subreddit = random.choice(b.subreddits)
    print(' >>> Going on r/{}'.format(subreddit))
    b.browser.get(b.getSubredditUrl(subreddit))
    b.disableSubStyle()
    posts = b.getVideoPosts()
    print(' >>> Found {} videos'.format(len(posts)))
    for index, post in enumerate(posts):
        print(' >> Post {}:'.format(index+1))
        try:
            button = post.find_element(By.CSS_SELECTOR, 'a.expando-button.collapsed.video')
            button.click()
            title = post.find_element(By.CSS_SELECTOR,'p.title').text
            print(' >> {}'.format(title))
            source = post.find_element(By.CSS_SELECTOR,'a.res-video-link.res-video-source')
            url = source.get_attribute('href')
            print(' >> {}'.format(url))
            button.click()
        except Exception as e:
            print(' >> FAIL'.format(title))
            print(e)
        
    b.cleanUp()
