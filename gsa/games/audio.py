from dataclasses import dataclass
import random

from .game import StatelessGame
from ..flower import Flower

@dataclass
class PlaySoundOnMultipleFlowers(StatelessGame):
    soundFile: str
    numFlowers: int = None  # How many flowers; if None, play on all flowers

    def run(self, flowers: 'list[Flower]'):
        if self.numFlowers is None:
            selectedFlowers = flowers
        else:
            numToSample = min(self.numFlowers, len(flowers))
            flowersCopy = list(flowers)
            random.shuffle(flowersCopy)
            selectedFlowers = flowersCopy[:numToSample]
        flowerNums = [f.num for f in selectedFlowers]
        print(f"Playing {self.soundFile} on {numToSample} flowers: {flowerNums}")
        for flower in selectedFlowers:
            flower.PlaySoundFile(self.soundFile)