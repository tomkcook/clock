# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 09:44:25 2013

@author: tom.cook
"""
import numpy as np
import numpy.linalg.linalg as li
import matplotlib.pylab as mp
import collections
import pygame.time as tm
import pygame.mixer as m

def change_from_places(p, order = 7):
    m = np.mat(np.zeros([order, order], int))
    i = 0
    while i < order:
        if i in p:
            m[i,i] = 1
            i += 1
        else:
            m[i,i+1] = 1
            m[i+1,i] = 1
            i += 2
    return m
    
def method_from_places(p, order = 7):
    lead_length = p.shape[0]
    m = []
    for i in range(0, lead_length):
        m.append(change_from_places(p[i], order))
    return m

def calls_from_places(m, bob_p = [], single_p = [], lead_heads=[0]):
    plain = m[(lead_heads[0]-1)%len(m)]
    order = plain.shape[0]
    if len(bob_p) > 0:
        bob = change_from_places(bob_p, order)
    else:
        bob = plain
    if len(single_p) > 0:
        single = change_from_places(single_p, order)
    else:
        single = plain
    plain_i = li.inv(np.matrix(plain))
    return [(plain_i*bob).astype(int), (plain_i*single).astype(int)]

def get_default_transition(t, order):
    if t == []:
        t = np.eye(order)
    return t
    
def get_transition(m, index, bob, single, calls, lead_heads):
    lead_length = len(m)
    index = index % lead_length
    t = m[index]
    if (index + 1) % lead_length in lead_heads:
        c = calls[0]
        calls.popleft()
        if len(calls) < 1:
            calls.append(0)
        if c > 0:
            t = t * bob
        elif c < 0:
            t = t * single
        else:
            pass
    return t

def step_method(m, last_change, index):
    pass

def iterate_method(t, s, index):
    p = s[:, index]
    p = t * p
    s = np.hstack([s, p])
    return s

def run_method(m, changes, bob, single, calls=[0], start_change=0, lead_heads=[0]):
    order = m[0].shape[0]
    bells = np.mat(range(0, order), int).transpose()
    s = np.mat(np.zeros([order, 1]), dtype=int)
    s[:,0] = bells
    for i in range(0, changes):
        t = get_transition(m, i, bob, single, calls, lead_heads)
        s = iterate_method(t, s, i)
    return s

def run_method_to_rounds(m, bob, single, calls=[0], start_change = 0, lead_heads=[0]):
    order = m[0].shape[0]
    bells = np.mat(range(0, order), int).transpose()
    s = np.mat(np.zeros([order, 1]), int)
    s = s.astype(int)
    s[:,0] = bells.astype(int)
    j = 0
    while (s[:, s.shape[1]-1] != bells).any() or s.shape[1] == 1:
        t = get_transition(m, j + start_change, bob, single, calls, lead_heads)
        s = iterate_method(t, s, j)
        j += 1
    return s.astype(int)

def rounds(order = 7, changes = 1):
    places = np.mat([range(0, order)], dtype=int)
    method = method_from_places(places, order)
    return run_method(method, changes-1, None, None, collections.deque([0]))

def method_parts(method_places, bob_places, single_places, order = 7):
    method = method_from_places(method_places, order)
    [bob, single] = calls_from_places(method, bob_places, single_places)
    return [method, bob, single]

def method(method_places, bob_places, single_places, calls = [0], order = 7):
    [method, bob, single] = method_parts(method_places, bob_places, single_places, order)
    return run_method_to_rounds(method, bob, single, collections.deque(calls), 9, [0, 6])
    
def stedman(order = 7, calls = [0]):
    stedman_places = np.mat([[2], [0], [2], [0], [2], [order-1], [0], [2], [0], [2], [0], [order-1]])
    stedman_bob = [order-3]
    stedman_single = [order-3, order-2, order-1]
    return method(stedman_places, stedman_bob, stedman_single)

def stedman_parts(order = 7):
    stedman_places = np.mat([[2], [0], [2], [0], [2], [order-1], [0], [2], [0], [2], [0], [order-1]])
    stedman_bob = [order-3]
    stedman_single = [order-3, order-2, order-1]
    return method_parts(stedman_places, stedman_bob, stedman_single)

def plot_method(s, lines = [], numbers = []):
    bells = s.shape[0]
    # Default is to print all lines and all numbers
    if len(lines) == 0:
        lines = range(0, bells)
    if len(numbers) == 0:
        numbers = range(0, bells)
    rounds = np.mat(range(0,bells)).astype(int).transpose()
    changes = s.shape[1]
    places = np.empty(s.shape, int)
    for i in range(0,changes):
        c = s[:,i]
        d = places[:,i]
        d[c] = rounds
    mp.plot(places[lines, :].transpose())
    mp.subplots_adjust(left=0.04, right=0.96, top = 0.9, bottom = 0.1)
    for i in numbers:
        for j in range(0,changes):
            mp.text(j, places[i, j], i+1, fontsize=16, horizontalalignment='center', verticalalignment='center')
    ticks = [2.5]
    while ticks[-1] < changes:
        ticks.append(ticks[-1] + 6)
    mp.xticks(ticks)
#    mp.grid(linestyle='-', linewidth=2)
    mp.gca().yaxis.grid(False)

def string_change(change):
    return "".join(str(change[i,0]) for i in range(0,7))
def array_change(change):
    return np.mat([int(c) for c in change], int).transpose()

def play_row(s, i, sounds, gap, covering):
    bells = s.shape[0]
    for j in range(bells):
        sounds[s[j, i]].stop()
        sounds[s[j, i]].play()
        tm.wait(gap)
    if covering:
        sounds[-1].stop()
        sounds[-1].play()
        tm.wait(gap)

def play_rounds(bells, sounds, gap, covering, rows = 2):
    r = rounds(bells, rows)
    play_method_matrix(r, sounds, gap, covering)
    
def play_method_matrix(s, sounds, gap, covering):
    rows = s.shape[1]
    for i in range(rows):
        play_row(s, i, sounds, gap, covering)
        if i % 2 == 1:
            tm.wait(gap)
            
def play_method(s, sounds, gap=300):
    bells = s.shape[0]
    covering = (bells % 2 == 1)
    play_rounds(bells, sounds, gap, covering, 4)
    play_method_matrix(s[:,1:], sounds,gap, covering)
    play_rounds(bells, sounds, gap, covering, 4)