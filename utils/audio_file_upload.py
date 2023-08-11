# This program uploads all audio files needed for the Field of Flowers to each flower.
#
# It works gradually. You start it, then wait and watch, and eventually all the flowers
# will have the right files.
#
# It knows about flowers by listening for ther heartbeats over MQTT (This program should
# run on the same network as the field and the MQTT broker; it doesn't need to be on the
# same host as the MQTT broker or other FEDs).
#
# For each flower that it has heard a heartbeat from, it will use FTP to check which fiels
# it already hase ("already has" means has a file with the same path and same size; we match
# size to defend against partial uplads).  If a file is missing or wrong-sized, then it
# is uploaded to that flower.
#
# It is given a source directory containing all the audio files, already converted into the
# correct format (see wav-fo-fof.py).
#
# This program will proceed gradually through the field, running ftp commands in separate
# processes, and limiting the total number of simultaneous operations in order to not
# overwhelm the network.
#
# Example usage:
#   python3 audio_file_upload.py /Users/jeff/fof/audio_files/prepped_for_flowers

from dataclasses import dataclass
import json
import ftplib
from threading import Thread
import os
from pathlib import Path
import random
import subprocess
import time
import sys
from typing import Dict, List, Callable

import paho.mqtt.client as mqtt

MQTT_BROKER_IP = "192.168.1.72"  # You may need to change this to 127.0.0.1
MAX_SIMULTANEOUS_FTP_THREADS = 10
# TODO: Make this a command line argument.
FTP_BINARY = "/usr/local/opt/tnftp/bin/ftp"

@dataclass
class AudioFile:
    path: Path  # relative to the reference directory, or the SD card root
    size: int   # bytes


def parseFileListLine(line: str) -> AudioFile:
    # This is very simple for now. Listing lines from the flower FTP serve look like this:
    # -rw-r--r-- 1 owner group         96974 Jan 01  1970 pb-rising-16.wav
    # We also get lots of othe lines, for error codes and other messages.
    if not isinstance(line, str):
        print(f"ERROR: Tried to parse a non-string: {line}")
        return None
    words = line.split()
    if len(words) > 0:
        filename = words[-1]
        if filename.lower().endswith(".wav"):
            filesize = None
            try:
                filesize = int(words[-5])
            except ValueError:
                pass
            return AudioFile(Path(filename), filesize)
    return None

# Represents a flower, including its heartbeat details and what is known about
# which audio files it has.
#   heartbeat_dict: result of parsing the JSON flower heartbeat. Contains the flower
#                      sequennce number and IP address.
#   referenceDir:   local dir on this machine where the audio files are stored. Used
#                      as the source dir for uploads
#   requiredFiles:  list of files needed for upload. Determined by scanning
#                     referenceDir when the program started
class Flower:
    def __init__(self, heartbeat_dict, referenceDir, requiredFiles):
        self.num = heartbeat_dict['sequence_num']
        self.heartbeat: Dict[str, str] = heartbeat_dict
        self.referenceDir: Path = referenceDir
        self.requiredFiles: List[AudioFile] = requiredFiles
        self.existingFiles: List[AudioFile] = None  # None means unknown

    def makeFTPClient(self) -> ftplib.FTP:
        return ftplib.FTP(host=self.heartbeat['IP'], user='fof', passwd='fof')

    def existingFilesKnown(self) -> bool:
        return self.existingFiles is not None
 
    def hasFile(self, targetFile: AudioFile):
        for existingFile in self.existingFiles:
            if existingFile.path == targetFile.path:
                # I tried a version that checked whether the file sizes match too,
                # but this didn't work; the flowers always report slightly different sizes
                # than the file system on the my laptop.
                return True
        return False

    def missingFiles(self) -> List[AudioFile]:
        if self.existingFiles is None:
            return None  # unknown
        return [f for f in self.requiredFiles if not self.hasFile(f)]
 
    def runFTPCommands(self, ftpCommands):
        url = 'ftp://fof:fof@' + self.heartbeat['IP']
        raw_output = subprocess.run([FTP_BINARY, url],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    input=ftpCommands.encode('utf-8')).stdout
        return raw_output.decode('utf-8').splitlines()

    def queryFilesInDirectory(self, directory):
        dirPath = Path('SD').joinpath(directory)
        # The mkdir fails harmlessly if the directory already exists.
        ftp_output = self.runFTPCommands(f'mkdir {dirPath}\ncd {dirPath}\ndir\nbye\n')
        foundFiles = []
        for line in ftp_output:
            audioFile = parseFileListLine(line)
            if audioFile is not None:
                audioFile.path = Path(directory).joinpath(audioFile.path)
                foundFiles.append(audioFile)
        return foundFiles

    def findOutExistingFiles(self):
        # Only supports 1-deep directories for now.  All audio files are either
        # in the SD folder (the root), or in a subdirectory of it, e.g. SD/fairy
        directories = ['/'] + list(set(f.path.parent for f in self.requiredFiles))
        print(f"Flower {self.num}: querying for existing files in directories: " + 
              ','.join(str(d) for d in directories))
        allFiles = []
        for directory in directories:
            allFiles.extend(self.queryFilesInDirectory(directory))
        self.existingFiles = allFiles
        print(f"Flower {self.num} has a total of {len(self.existingFiles)} audio files " +
              f"and is missing {len(self.missingFiles())} audio files.")

    def uploadOneNeededFile(self):
        fileToUpload = random.choice(self.missingFiles())
        subdir = Path('SD').joinpath(fileToUpload.path.parent)
        print(f"Flower {self.num}: Uploading {str(fileToUpload.path)}")
        full_source_path = self.referenceDir.joinpath(fileToUpload.path).absolute()
        full_target_path = Path('SD').joinpath(fileToUpload.path)
        self.runFTPCommands(f'mkdir {subdir}\nput {full_source_path} {full_target_path}\nbye\n')
        # There doesn't seem to be any way to confirm the upload worked, so assume it did
        # We'll verify later with a full listing.
        self.existingFiles.append(fileToUpload)


def SetupMQTTClient(flowers, referenceAudioFileDir, requiredFiles):
    # Required by paho, but unused
    def on_pre_connect(unused_arg1, unused_arg2):
        pass

    def on_connect(client, unused_userdata, unused_flags, result_code):
        result = "successfull." if result_code == 0 else "FAILED!"
        print(f'Connection to MQTT broker at {MQTT_BROKER_IP} {result}')
        print('Subscribing to flower heartbeat messages.')
        client.subscribe("flower-heartbeats/#")

    def on_message(unused_client, unused_userdata, message):
        heartbeat = json.loads(message.payload.decode('utf8'))
        flower_num = int(heartbeat['sequence_num'])
        if flower_num not in flowers:
            flowers[flower_num] = Flower(
                heartbeat, referenceAudioFileDir, requiredFiles)

    def on_disconnect(unused_client, unused_userdata, result_code):
        if result_code != 0:
            print("Unexpected MQTT disconnection.")

    client = mqtt.Client(client_id="fake_flowers")
    client.on_pre_connect = on_pre_connect
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(MQTT_BROKER_IP)
    # Caller is responsible for calling client.loop() to handle received messages
    return client


# Traverse the reference directory for all .wav files, making a list of each
# of them (the path relative to the dir), paired with its size in bytes.
def readRequiredFiles(referenceDir: Path) -> List[AudioFile]:
    results = []
    for root, unused_dirs, files in os.walk(referenceDir):
        for filename in files:
            if filename.lower().endswith(".wav"):
                path = Path(root).joinpath(filename)
                size = os.path.getsize(path)
                results.append(AudioFile(path.relative_to(referenceDir), size))
    return results


def printProgressSummary(flowers: List[Flower]):
    numKnown, numWithMissing, totalMissingFiles, totalMissingBytes = 0, 0, 0, 0
    for flower in flowers:
        if flower.existingFilesKnown():
            numKnown += 1
            missingFiles = flower.missingFiles()
            numWithMissing += 1 if missingFiles else 0
            totalMissingFiles += len(missingFiles)
            totalMissingBytes += sum(f.size for f in missingFiles)
    print(f"\n{'*'*30} Progress {'*' * 30}")
    print(f"*   Seen heartbeats from {len(flowers)} flowers.")
    print(f"*   {numKnown} flowers have been queried for their current files.")
    print(f"*   {totalMissingFiles} total files totalling {round(totalMissingBytes/1024)}" +
                f" KB still need to be uploaded.")
    print(f"*   {numKnown-numWithMissing}/{len(flowers)} flowers have all needed files.")
    print('*' * 70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Requires one argument specifying the reference directory.")
        sys.exit()
    referenceAudioFileDir = Path(sys.argv[1])

    requiredFiles = readRequiredFiles(referenceAudioFileDir)
    totalBytes = sum(rf.size for rf in requiredFiles)
    print(f"Read {len(requiredFiles)} audio files ({totalBytes} total bytes) from {referenceAudioFileDir}.")

    # Keyed by flower sequence number (so we can only upload to flowers that have been
    # flashed with firmwhere that includes themselves.)
    flowers: Dict[int, Flower] = {}

    mqtt_client = SetupMQTTClient(flowers, referenceAudioFileDir, requiredFiles)
    mqtt_client.loop_start()

    # Pool of thread for running ftp operations asyncronously.
    ftpThreads: List[Thread] = []
 
    lastProgressSummaryTime: float = time.time()  # Seconds since epoch

    def startFTPThread(flower: Flower, target: Callable):
        if len(ftpThreads) > MAX_SIMULTANEOUS_FTP_THREADS:
            return
        flowers_nums_with_active_threads = [thread.name for thread in ftpThreads]
        if flower.num in flowers_nums_with_active_threads:
            # The flower FTP servers can only handle a single client connection at once.
            return
        thread = Thread(target=target, name=flower.num)
        thread.start()
        ftpThreads.append(thread)

    while True:
        # If we have flowers without known contents, find out what they have
        for flower in flowers.values():
            if not flower.existingFilesKnown():
                # Only starts if no other process is already running for this flower.
                startFTPThread(flower, flower.findOutExistingFiles)

        # If we need to upload anything, upload it.
        for flower in flowers.values():
            if flower.existingFilesKnown() and flower.missingFiles():
                # Only starts if no other process is already running for this flower.
                startFTPThread(flower, flower.uploadOneNeededFile)
        
        # Clean up finished threads
        finishedFTPThreads = [t for t in ftpThreads if not t.is_alive()]
        for thread in finishedFTPThreads:
            ftpThreads.remove(thread)

        if time.time() - lastProgressSummaryTime > 10:
            printProgressSummary(flowers.values())
            lastProgressSummaryTime = time.time()

        # Most FTP threads take a few seconds to a few minutes to run, so we don't need
        # to poll very often.
        time.sleep(0.5)  # seconds
