# The MIT License (MIT)
# Copyright (c) 2022 Mike Teachman
# https://opensource.org/licenses/MIT

# Purpose:  Play a WAV audio file out of a speaker or headphones
#
# PB added:
#  -- network connection
#  -- onboard LED blinking with timer
#
# TODO:
#   -- get packet over wifi, do something
#   -- blink Dotstars in some way
#   -- confirm neither audio nor LEDs glitch


import os
import network
import micropython
from machine import I2S, Pin, Timer

SCK_PIN = 27    # orig 32 - BCLK
WS_PIN = 26     # orig 25 - WSEL
SD_PIN = 25     # orig 33 - DIN
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 5000

# ======= AUDIO CONFIGURATION =======
WAV_FILE = "pbtones.wav"
WAV_SAMPLE_SIZE_IN_BITS = 16
FORMAT = I2S.MONO
SAMPLE_RATE_IN_HZ = 8000
# ======= AUDIO CONFIGURATION =======

audio_out = I2S(
    I2S_ID,
    sck=Pin(SCK_PIN),
    ws=Pin(WS_PIN),
    sd=Pin(SD_PIN),
    mode=I2S.TX,
    bits=WAV_SAMPLE_SIZE_IN_BITS,
    format=FORMAT,
    rate=SAMPLE_RATE_IN_HZ,
    ibuf=BUFFER_LENGTH_IN_BYTES,
)

led = Pin(2, Pin.OUT)   # onboard blue LED
led_timer = Timer(1)

# allocate sample array
# memoryview used to reduce heap allocation
wav_samples = bytearray(1000)
wav_samples_mv = memoryview(wav_samples)


def toggle_led(t):
    led.value(not led.value())


def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('FBI Surveillance Van', 'pigs4food')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())


def run():
    print("run begins")

    led_timer.init(mode=Timer.PERIODIC, period=1000, callback=toggle_led)
    print(micropython.mem_info())

    do_connect()

    print("opening wav file")
    wav = open(WAV_FILE, "rb")
    pos = wav.seek(44)  # advance to first byte of Data section in WAV file

    led_on = False

    while True:
        num_read = wav.readinto(wav_samples_mv)
        # end of WAV file?
        if num_read == 0:
            # end-of-file, advance to first byte of Data section
            _ = wav.seek(44)
        else:
            _ = audio_out.write(wav_samples_mv[:num_read])

    # cleanup
    wav.close()
    audio_out.deinit()
    print("Done")

# done.
