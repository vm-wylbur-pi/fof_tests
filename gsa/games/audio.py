from dataclasses import dataclass
import random

from .game import StatelessGame
from ..game_state import GameState
from typing import List

@dataclass
class PlaySoundOnMultipleFlowers(StatelessGame):
    soundFile: str
    syncToControlClock: bool
    numFlowers: int = None  # How many flowers; if None, play on all flowers

    def run(self, gameState: GameState):
        if self.numFlowers is None:
            selectedFlowers = gameState.flowers
        else:
            numToSample = min(self.numFlowers, len(gameState.flowers))
            flowersCopy = list(gameState.flowers)
            random.shuffle(flowersCopy)
            selectedFlowers = flowersCopy[:numToSample]
        flowerNums = [f.num for f in selectedFlowers]
        print(f"Playing {self.soundFile} on {numToSample} flowers: {flowerNums}")
        for flower in selectedFlowers:
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
