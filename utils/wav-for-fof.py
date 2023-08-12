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
import shutil
import logging
import tempfile


def getargs():
    parser = argparse.ArgumentParser(
            prog='wav_for_fof',
            description="converts wav files to encoding=pcm_s16le, sample freq=16k/s, mono")
    parser.add_argument("-v", "--verbose", action='count', default=0)
    parser.add_argument('src_dir')
    parser.add_argument('dest_dir')
    args = parser.parse_args()
    args.src_dir = Path(args.src_dir)
    assert args.src_dir.exists()
    if args.verbose > 0:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    return args

def convert_one(wav):
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    tmpname = Path(tmpfile.name + ".wav")
    subprocess.run(
        ['ffmpeg', '-y', '-i', wav,
         '-hide_banner', '-loglevel', 'error',
         '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le',
         tmpname])
    shutil.move(tmpname, wav)
    logging.debug(f"converting {wav}")


if __name__ == '__main__':
    args = getargs()

    shutil.copytree(args.src_dir, args.dest_dir, dirs_exist_ok=True)

    for wav in Path(args.dest_dir).rglob("*.wav"):
        convert_one(wav)

# done.
