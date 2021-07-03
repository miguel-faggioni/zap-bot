#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Resize and add text to videos

Usage example:
  $ python transform.py

"""

import random
import os
import shutil
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from sqlite import *

class VideoTransform:
    def __init__(self, videos=[]):
        print(' ----> {} videos to transform'.format(len(videos)))
        for video in videos:
            video['clip'] = VideoFileClip(video['filepath'])
        self.videos = videos
        print(' --> {} videos converted to clips'.format(len(self.videos)))

    def adjustSize(self, clip,width,height):
        # get current dimensions and ratio
        clipWidth,clipHeight = clip.size
        ratio = clipWidth / clipHeight
        # resize the clip
        if ratio > (width/height):
            clip2 = clip.resize(width=width)
        else:
            clip2 = clip.resize(height=height)
        return clip2
        
    def adjustSizes(self,width=1920,height=1080):
        for video in self.videos:
            video['clip'] = self.adjustSize(video['clip'],width,height)

    def addSubtitle(self, clip, subtitle, howLong, maxLength=15):
        # trim the subtitle if it's too long
        if len(subtitle) > maxLength:
            subtitle = subtitle[:maxLength] + '...'
        # set how long the subtitle will show
        howLong = min(howLong,clip.duration)
        subs = [((0, howLong), subtitle)]
        # create clip with subtitle
        subtitles = SubtitlesClip(subs, lambda txt: TextClip(txt, font='Arial', fontsize=72, color='white', stroke_color='black'))
        # merge clip and subtitles
        result = CompositeVideoClip([clip, subtitles.set_position(('center','bottom'))])
        # return resulting clip
        return result

    def addSubtitles(self, howLong=10):
        print(' ----> Adding subtitles')
        for index, video in enumerate(self.videos):
            video['clip'] = self.addSubtitle(video['clip'],video['title'],howLong)
            print(' --> {}/{} subtitles added'.format(index+1,len(self.videos)))

    def addSource(self,clip,source,howLong):
        howLong = min(howLong,clip.duration)
        subs = [((0, howLong), source)]        
        # create clip with source
        subtitles = SubtitlesClip(subs, lambda txt: TextClip(txt, font='Arial', fontsize=24, color='white', bg_color='black'))
        # merge clip and text
        result = CompositeVideoClip([clip, subtitles.set_position((0,0))])
        # return resulting clip
        return result

    def addSources(self, howLong=10):
        print(' ----> Adding sources')
        for index, video in enumerate(self.videos):
            video['clip'] = self.addSource(video['clip'],video['link'],howLong)
            print(' --> {}/{} sources added'.format(index+1,len(self.videos)))
            
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

    # add subtitles
    transform.addSubtitles()
    
    # add link to original
    transform.addSources()

    # backup the original videos 
    # and save the updated versions
    for video in transform.videos:
        shutil.move(video['filepath'],video['filepath']+'.original')
        transform.save(video['clip'],video['filepath'])
    
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
        '''.format(
            duration=duration,
            filepath=filepath,
            width=width,
            height=height
        ))
        
