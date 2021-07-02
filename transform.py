#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Resize and add text to videos

Usage example:
  $ python transform.py

"""

import random
import os
from moviepy.editor import *
from sqlite import *

class VideoTransform:
    def __init__(self, videos=[]):
        for video in videos:
            video['clip'] = VideoFileClip(video['filepath'])
        self.videos = videos
        print(' --> {} videos converted to clips'.format(len(self.videos)))

    def adjustSizes(self):
        resizedClips = []
        for video in self.videos:
            clip = video['clip']
            # get current dimensions and ratio
            clipWidth,clipHeight = clip.size
            ratio = clipWidth / clipHeight
            # resize the clip
            if ratio > (16/9):
                clip2 = clip.resize(width=1920)
            else:
                clip2 = clip.resize(height=1080)
            resizedClips.append(clip2)
            video['clip'] = clip2

    def addSubtitle(self, clip, subtitle):
        pass

    def save(self, clip, filename, threads=1):
        filepath = os.path.join(os.getcwd(),filename)
        clip.write_videofile(filepath, codec='mpeg4', audio=True, threads=threads)
        return filepath

    
if __name__ == '__main__':
    # get videos from DB
    sql = Sqlite()
    result = sql.run('SELECT * FROM videos WHERE duration IS NULL')
    videos = [ row for row in result ]

    # convert them to clips
    transform = VideoTransform(videos)

    # resize them
    transform.adjustSizes()
    
    # update their durations and sizes on the DB
    for video in transform.videos:
        filepath = video['filepath']
        duration = video['clip'].duration
        width,height = video['clip'].size
        sql.run('''
            UPDATE videos 
            SET duration = {duration},
                width    = {width},
                height   = {height}
            WHERE 
                filepath = '{filepath}'
        '''.format(duration=duration,filepath=filepath,width=width,height=height))

    # add subtitle

    # add link to original

    # save the updated video
    for video in transform.videos:
        pass#transform.save(video['clip'],video['filepath'])
        

    
