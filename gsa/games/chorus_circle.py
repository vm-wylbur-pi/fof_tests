import random
import time
from typing import List, Dict

from . import game
from ..game_state import GameState
from ..flower import Flower
from ..color import HSVAColor

# Every now and then, a group of six flowers somewhere in the field will have
# short singing session, in which one flower starts singing, then others follow,
# riffirng variations on the first melody.
class ChorusCircle(game.StatefulGame):

    # How long the first flower sings before the 2nd comes in.
    FIRST_PART_DELAY = 3000
    # How long each subsequent flower sings before the one after it starts.
    REST_OF_PARTS_DELAY = 2000

    def __init__(self, gapBetweenSongs: int = 30, volume: float = 5.0):
        # Behavior variables.  Constant for any game instance.
        self.gapBetweenSongs: float = gapBetweenSongs  # Seconds
        self.volume: float = volume
        self.audioFiles: Dict[str, List[str]] = game.getAudioFiles()['ChorusCircle']
        # State variables
        self.nextSongTime: float = 0  # seconds since epoch, as returned by time.time()
        self.lastSingers: List[Flower] = None
        self.backgroundColor = HSVAColor(random.randint(0, 255), 100, 100, 255)
        self.firstRun = True

    def runLoop(self, gameState: GameState):
        if self.firstRun:
            for flower in gameState.flowers:
                flower.SetBlossomColor(self.backgroundColor)
            self.firstRun = False

        now = time.time()
        if now > self.nextSongTime:
            
            if self.lastSingers is not None:
                print(f"resetting last singers: {self.lastSingers}")
                for flower in self.lastSingers:
                    flower.SetBlossomColor(self.backgroundColor)

            # Chose where to have the chorus:
            startingFlower = None
            person = gameState.people.pickOneAtRandom()
            if person:
                startingFlower = gameState.closestFlowerTo(person.location)
            else:
                startingFlower = random.choice(gameState.flowers)

            otherSingers = startingFlower.findNClosestFlowers(gameState.flowers, 5)
            singers = [startingFlower] + otherSingers
            parts = random.choice(list(self.audioFiles.values()))
            # brighter and more saturated than the background
            chorusColor = HSVAColor(random.randint(0, 255), 255, 250, 255)

            print(f"Starting chorus on flowers {[f.num for f in singers]} singing {parts}")
            delay = 0
            for i, (singer, part) in enumerate(zip(singers, parts)):
                singer.SetVolume(self.volume)
                singer.SetBlossomColor(chorusColor)
                singer.PlaySoundFile(part, gameState.controlTimer() + delay)
                delay += (ChorusCircle.FIRST_PART_DELAY if i==0 else ChorusCircle.REST_OF_PARTS_DELAY)

            self.lastSingers = singers
            self.nextSongTime = now + self.gapBetweenSongs
