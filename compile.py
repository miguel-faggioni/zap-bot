#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Join videos into a compilation video

Usage example:
  $ python compile.py

"""

import random
import os
from moviepy.editor import *
from sqlite import *

COMPILATION_FOLDER = 'compilations'

class VideoCompilation:
    def __init__(self, videos=[]):
        self.clips = [ VideoFileClip(video) for video in videos ]
        print(' --> {} clips'.format(len(self.clips)))

    def save(self, clip, filename, threads=1):
        filepath = os.path.join(os.getcwd(),filename)
        clip.write_videofile(filepath, codec='mpeg4', audio=True, threads=threads)
        return filepath
    
    def createCompilation(self, max_total_time=None):
        # max_total_time is in seconds
        durations = [ clip.duration for clip in self.clips ]
        total_time = sum(durations)

        # keep only clips up to max total time
        if max_total_time is not None and total_time > max_total_time:
            partialTimes = list(itertools.accumulate(durations))
            firstOverMax = [ duration > max for duration in partialTimes ].index(True)
            clips = self.clips[:firstOverMax]
        else:
            clips = self.clips

        print(' ----> Creating compilation with {} clips'.format(len(clips)))
            
        # create compilation
        compilation = concatenate_videoclips(clips, method='compose')
        return compilation



def randomSubset(arr, length):
    indexes = random.sample(range(len(arr)), length)
    return [ item for (index,item) in enumerate(arr) if index in indexes]
    
if __name__ == '__main__':
    # get videos from DB
    sql = Sqlite()
    result = sql.run('''
        SELECT * FROM videos
        WHERE 
            compilation IS NULL 
            AND duration < {max_duration} 
            AND (
                original_width >= {min_width}
                OR original_height >= {min_height}
            )
    '''.format(
        max_duration=60,
        min_width=1280,
        min_height=720
    ))
    videos = [ row['filepath'] for row in result ]

    # get a random subset of the videos
    videos = randomSubset(videos, 30)
    
    # start the compilation
    compilation = VideoCompilation(videos)

    # create compilation of up to 30min
    video = compilation.createCompilation(30*60)

    # count how many compilations still exist
    rows = sql.run('SELECT COUNT(DISTINCT compilation) AS compilations FROM videos')
    existingCount = [ row for row in rows ][0]['compilations']
    
    # generate compilation filename
    compilation_filename = 'compilation_{}.mp4'.format(existingCount+1)
    
    # save it
    compilation.save(video,os.path.join(COMPILATION_FOLDER,compilation_filename),threads=2)

    # update the videos on the DB
    sql = Sqlite()
    for video in videos:
        filepath = video
        sql.run('''
            UPDATE videos 
            SET compilation = '{compilation}'
            WHERE 
                filepath = '{filepath}'
        '''.format(
            compilation=compilation_filename,
            filepath=filepath
        ))
