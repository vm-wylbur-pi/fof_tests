#!/usr/bin/env python3
#
# Author: PB
# Maintainer(s): PB
# License: (c) wylbur 2023, GPL v2 or newer
# ------------------------------------
# utils/wav-for-fof.py
#

from pathlib import Path
import argparse
import os
import logging
import subprocess


def getargs():
    parser = argparse.ArgumentParser(
            prog='wav_for_fof',
            description="converts wav files to encoding=pcm_s16le, sample freq=16k/s, mono")
    parser.add_argument('src_dir')
    parser.add_argument('dest_dir')
    args = parser.parse_args()
    args.src_dir = Path(args.src_dir)
    assert args.src_dir.exists()
    return args


if __name__ == '__main__':
    args = getargs()

    wavs = [f for f in os.listdir(args.src_dir)
            if Path(args.src_dir, f).is_file()]

    for wav in wavs:
        # logger.info(f"converting {Path(args.src_dir, wav} --> {Path(args.dest_dir, wav)}")

        subprocess.run(
                ['ffmpeg', '-i', Path(args.src_dir, wav),
                 '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le',
                 Path(args.dest_dir, wav)])

# done.
