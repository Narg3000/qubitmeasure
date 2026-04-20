# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 15:33:26 2022

@author: Guang Yue

Edited on 4/17/2026 by Autumn Bauman
"""
import numpy as np



def gauss_wave(t, f, sd, x0, p0):  # ns, MHz, Pi
    p = np.exp(-0.5 * (t - x0) ** 2 / sd ** 2)
    s = np.sin(2 * np.pi * f * t * 0.001 + np.pi * p0)
    return p * s




def g_waveform(delay, length, f, sd, p0, amp, offset):  # unit ns, MHz, Pi
    w = np.array([])
    for x in range(length):
        w = amp * np.append(w, gauss_wave(x, f, sd, delay, p0) + offset)
    return w.tolist()


def dc_waveform(delay, length, f, p0, amp, offset):  # unit ns, MHz, Pi, length includes delay
    w = np.array([])
    for x in range(delay):
        w = np.append(w, offset)
    for x in range(length - delay):
        w = np.append(w, amp * np.sin(2 * np.pi * f * 0.001 * (delay + x) + p0) + offset)
    return w.tolist()


def dc_t2_waveform(delay, length, f, p0, amp, offset, t2_m):  # unit ns, MHz, Pi, pulse length(no delay), time t2
    w = np.array([])
    length = int(length)
    for x in range(delay):
        w = np.append(w, offset)
    for x in range(length):
        w = np.append(w, amp * np.sin(2 * np.pi * f * 0.001 * (delay + x) + p0) + offset)
    for x in range(t2_m):
        w = np.append(w, offset)
    for x in range(length):
        w = np.append(w, amp * np.sin(2 * np.pi * f * 0.001 * (delay + length + t2_m + x) + p0) + offset)
    return w.tolist()


def zero_waveform(length, offset):  # assuming 1ns per point
    w = np.array([])
    for x in range(length):
        w = np.append(w, offset)
    return w.tolist()


"""
Test Code
w=np.array([])
for x in range(1500):
    w=np.append(w,libqubit.gauss_wave(x*0.001, 50, 0.05,1,1))


"""
