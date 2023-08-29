from dataclasses import dataclass
import random

from .game import StatelessGame
from ..game_state import GameState
from typing import List

@dataclass
class PlaySoundOnMultipleFlowers(StatelessGame):
    soundFile: str
    # Gain sync at the cost of latency. latency only matters for stuff
    # like interactive reactions or the DoJ interface.
    syncToControlClock: bool = True
    numFlowers: int = None  # How many flowers; if None, play on all flowers

    # More gives more time for all flowers to get the message (better sync),
    # but adds overall latency to the effect. 
    SYNC_LATENCY_MILLIS = 200

    def run(self, gameState: GameState):
        if self.numFlowers is None:
            selectedFlowers = gameState.flowers
        else:
            numToSample = min(self.numFlowers, len(gameState.flowers))
            flowersCopy = list(gameState.flowers)
            random.shuffle(flowersCopy)
            selectedFlowers = flowersCopy[:numToSample]
        flowerNums = [f.num for f in selectedFlowers]
        print(f"Playing {self.soundFile} on {len(selectedFlowers)} flowers: {flowerNums}")
        syncTime = gameState.controlTimer() + PlaySoundOnMultipleFlowers.SYNC_LATENCY_MILLIS
        for flower in selectedFlowers:
            if self.syncToControlClock:
                flower.PlaySoundFile(self.soundFile, startTime=syncTime)
            else:
                flower.PlaySoundFile(self.soundFile)


# Distribute a set of sound files evenly across the field
@dataclass
class PlaySoundSetAcrossField(StatelessGame):
    soundFiles: List[str]

    def run(self, gameState: GameState):
        for i, flower in enumerate(gameState.flowers):
            soundFile = self.soundFiles[i % len(self.soundFiles)]
            flower.PlaySoundFile(soundFile)
            #print(f"Playing {soundFile} on flower {flower.num}.")
