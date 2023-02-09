# The MIT License (MIT)
# Copyright (c) 2022 Mike Teachman
# https://opensource.org/licenses/MIT
# https://github.com/miketeachman/micropython-i2s-examples/blob/master/examples/play_wav_from_sdcard_non_blocking.py
#
# Purpose:  Play a WAV audio file out of a speaker or headphones
#
# - read audio samples from a WAV file on SD Card
# - write audio samples to an I2S amplifier or DAC module
# - the WAV file will play continuously in a loop until
#   a keyboard interrupt is detected or the board is reset
#
# non-blocking version
# - the write() method is non-blocking.
# - a callback function is called when all sample data has been written to the I2S interface
# - a callback() method sets the callback function

import os
import time
import micropython
from machine import I2S
from machine import Pin, Timer

SCK_PIN = 27    # orig 32 - BCLK
WS_PIN = 26     # orig 25 - WSEL
SD_PIN = 25     # orig 33 - DIN
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 5000

# ======= AUDIO CONFIGURATION =======
WAV_SAMPLE_SIZE_IN_BITS = 16
FORMAT = I2S.MONO
SAMPLE_RATE_IN_HZ = 16000
# ======= AUDIO CONFIGURATION =======
PLAY = 0
PAUSE = 1
RESUME = 2
STOP = 3
led = Pin(2, Pin.OUT)


def eof_callback(arg):
    global state
    print("end of audio file")
    # state = STOP  # uncomment to stop looping playback


def i2s_callback(arg):
    global state
    if state == PLAY:
        led.value(1)
        num_read = wav.readinto(wav_samples_mv)
        # end of WAV file?
        if num_read == 0:
            # end-of-file, advance to first byte of Data section
            pos = wav.seek(44)
            _ = audio_out.write(silence)
            micropython.schedule(eof_callback, None)
        else:
            _ = audio_out.write(wav_samples_mv[:num_read])

    elif state == RESUME:
        led.value(0)
        state = PLAY
        _ = audio_out.write(silence)

    elif state == PAUSE:
        led.value(0)
        _ = audio_out.write(silence)

    elif state == STOP:
        led.value(0)
        # cleanup
        wav.close()
        audio_out.deinit()
        print("Done")
    else:
        print("Not a valid state.  State ignored")


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

audio_out.irq(i2s_callback)
state = PAUSE

# allocate a small array of blank samples
silence = bytearray(1000)

# allocate sample array buffer
wav_samples = bytearray(10000)
wav_samples_mv = memoryview(wav_samples)


def run():

    # "music-16k-16bits-mono.wav"
    WAV_FILE = [f for f in os.listdir() if f.endswith(".wav")][0]

    wav = open(WAV_FILE, "rb")
    _ = wav.seek(44)  # advance to first byte of Data section in WAV file
    _ = audio_out.write(silence)
    print("wrote silence block")

    # add runtime code here ....
    # changing 'state' will affect playback of audio file

    print("starting playback for 10s")
    state = PLAY
    time.sleep(10)

    state = PAUSE
    time.sleep(10)
    print("resuming playback for 15s")
    state = RESUME
    time.sleep(15)
    print("stopping playback")
    state = STOP

# done.
