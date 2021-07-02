#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Resize and join short videos into a compilation video

Usage example:
  $ python compile.py

"""

import random
import os
from moviepy.editor import *

VIDEO_FOLDER = 'videos'

class VideoCompilation:
    def __init__(self, videos=[]):
        self.clips = [ VideoFileClip(video) for video in videos ]
        print(' --> {} clips'.format(len(self.clips)))

    def removeLongClips(self, max_clip_duration):
        # max_clip_duration is in seconds
        self.clips = [ clip for clip in self.clips if clip.duration <= max_clip_duration ]
        print(' --> {} clips shorter than {} seconds'.format(len(self.clips),max_clip_duration))

    def adjustSizes(self):
        resizedClips = []
        for clip in self.clips:
            # get current dimensions and ratio
            clipWidth,clipHeight = clip.size
            ratio = clipWidth / clipHeight
            # resize the clip
            if ratio > (16/9):
                clip2 = clip.resize(width=1920)
            else:
                clip2 = clip.resize(height=1080)
            resizedClips.append(clip2)
        self.clips = resizedClips

    def addSubtitle(self, clip, subtitle):
        pass

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
    # get videos from folder
    videos = [ file.path for file in os.scandir(os.path.join(os.getcwd(),VIDEO_FOLDER)) if file.is_file() and '.mp4' in file.path ]

    # get a random subset of the videos
    videos = randomSubset(videos, 30)
    
    # start the compilation
    compilation = VideoCompilation(videos)

    # remove videos longer than 2min
    compilation.removeLongClips(2*60)

    # resize clips
    compilation.adjustSizes()

    # create compilation of up to 30min
    video = compilation.createCompilation(30*60)

    # save it
    compilation.save(video,'first_compilation.mp4',threads=2)
