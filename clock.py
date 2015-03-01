#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
/home/tkcook/.spyder2/.temp.py
"""

import pygame.mixer as mx
import pygame.time as tm
from datetime import datetime, time, timedelta
import math
import ringing
import threading
import web_ringing

# Setting the buffer size to 2048 greatly improves the striking.  Not clear why.
mx.init(44100, -16, 2, 2048)

sounds = [mx.Sound('./data/bell-{0}.wav'.format(i)) for i in range(1,9)]
stedman = ringing.stedman()
ringing_vol = 0.25

# Set this for the pace you want the quarters chimed at
clock_period = 700
# Cambridge quarters
quarters = [
    [2, 3, 4, 7],
    [4, 2, 3, 7, 4, 3, 2, 4],
    [2, 4, 3, 7, 7, 3, 2, 4, 2, 3, 4, 7],
    [4, 2, 3, 7, 4, 3, 2, 4, 2, 3, 4, 7, 7, 3, 2, 4],
    ]

# Ring rounds - not currently used
def round():
    for i in range(8):
        sounds[i].play()
        tm.wait(250)

# Decide whether chimes should sound based on hour of day.
def quietTimes(h):
    return h > 6 and h < 22

# Chime four notes in the chime sequence.
# This treats the sequence as being in 3/4 time.  The first three are crotchets,
# the last a dotted minim.
def part(slice):
    for i in range(3):
        sounds[slice[i]-1].play()
        tm.wait(clock_period)
    sounds[slice[3]-1].play()
    tm.wait(clock_period*3)

# Chime the given quarter (1, 2, 3 or 4)
def quarter(n):
    for i in range(n):
        start = i*4
        end = (i+1)*4
        slice = quarters[n-1][start:end]
        part(slice)

# Chime the hour
def hour(n):
    for i in range(n):
        sounds[7].play()
        tm.wait(3000)

# Chime the quarters and hour as appropriate
def chime(n, h):
    if quietTimes(h):
        quarter(n)
        tm.wait(1500)
        if n == 4:
            if h > 12:
                hour(h-12)
            else:
                hour(h)

# This finds the next quarter-hour
def nextChimeTime():
    dt = datetime.today()
    nsecs = dt.minute*60 + dt.second + dt.microsecond*1e-6
    delta = (nsecs//900)*900+900-nsecs
    return dt + timedelta(seconds = delta)

def setVolume(vol):
    for s in sounds:
        s.set_volume(vol)

web_lock = threading.Lock()
web_method = None

def ring_method(name):
    global web_method
    global web_lock
    web_lock.acquire()
    web_method = name
    web_lock.release()

web_ringing.start(ring_method)

def check_ring_method():
    global web_lock
    global web_method
    web_lock.acquire()
    local_method = web_method
    web_lock.release()
    if local_method is not None:
        setVolume(ringing_vol)
        ringing.play_method(stedman, sounds)
        setVolume(1.0)
    web_lock.acquire()
    web_method = None
    web_lock.release()
    
while True:
    cTime = nextChimeTime()
    n = int(math.floor(cTime.minute/15))
    if n == 0:
        n = 4
    h = cTime.hour
    while datetime.today() < cTime:
        tm.wait(1000)
        check_ring_method()
    if (datetime.today() - cTime).total_seconds() < 60:
        chime(n, h)
