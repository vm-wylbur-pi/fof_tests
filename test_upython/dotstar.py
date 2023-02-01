# set expandtab ts=4 sw=4 ai fileencoding=utf-8
# micropython: run with pyboard.py
#
# Author: PB
# Maintainer(s): PB
# License: (c) PB 2023, GPL v2 or newer
#
# requires the https://github.com/mattytrentini/micropython-dotstar library
# -----------------------------------------------------------
#
import time
import random
import dotstar as dotstar
from machine import Pin, SPI
from utime import ticks_us, ticks_diff

# notes:
# * totally flaky if baud>10Mbs (nb Neopixels are 400Kbs)

spi = SPI(1, 10000000,
        sck=Pin(18), mosi=Pin(23), miso=Pin(13))  # note: miso is unused
dots = dotstar.DotStar(spi, 31, brightness=0.2, auto_write=False)

# HELPERS
# a random color 0 -> 224
def random_color():
    return random.randrange(0, 7) * 32


def fb2bb(fb):
    # 0-1 brightness to 0-31
    return 32 - int(32 - fb * 31)


def bb2fb(bb):
    if bb < 1:
        bb = bb * 100
    return bb * 0.03125


def dither_set(frac_bright, indices):
    # This is a hacked PWM.
    # Dotstar LEDs have a 5-bit brightness setting for each pixel.
    # given a 5bit floor brightness + a fractional brightness,
    # and a set of indices, assign at random a fraction of LEDs to be hi
    # and the rest lo.
    # return a tuple({indices lo}, {indices hi})
    ind_hi = {i for i in indices if random.random() < frac_bright}
    ind_lo = indices - ind_hi
    return (ind_lo, ind_hi)


print("SPI:")
print(spi)

bounds = {0, 10, 20, 30}
g1 = set(range(1, 10))
g2 = set(range(11, 20))
g3 = set(range(21, 30))

# let's pick 2 brightnesses:
b1 = bb2fb(1)
b2 = bb2fb(2)
print("b1=", b1, ", b2=", b2)

up = True
loops = 0
n_dots = len(dots)
start = ticks_us()

while True:
    loops += 1
    if loops > 500:
        elapsed = ticks_diff(ticks_us(), start)/1e6
        print("loops/sec = ", int(loops/elapsed))
        start = ticks_us()
        loops = 0

    g1_ind_lo, g1_ind_hi = dither_set(0.5, g1)
    g2_ind_lo, g2_ind_hi = dither_set(0.5, g2)

    # minimal function, 10Mbs rate = 110 loops/sec
    for dot in range(n_dots):
        if dot in bounds:
            dots[dot] = (255, 0, 0, b1)

        elif dot in g1:
            if dot in g1_ind_lo:
                dots[dot] = (0, 255, 0, 0)
            else:
                dots[dot] = (0, 255, 0, b1)

        elif dot in g2:
            if dot in g2_ind_lo:
                dots[dot] = (0, 255, 0, b1)
            else:
                dots[dot] = (0, 255, 0, b2)

        elif dot in g3:
            dots[dot] = (0, 255, 0, b2)

    dots.show()

# done.
