from dataclasses import dataclass

from .game import StatelessGame
from ..flower import Flower

@dataclass
class RunningLight(StatelessGame):
    startTime: int
    flowersPerSec: float = 15
    hue: int = 0
    sound: str = None

    def sortFlowers(self, flowers: 'list[Flower]'):
        # This part could be more interesting, if we sorted the flowers
        # in other ways.  (Maybe subclasses?)
        flowers.sort(key=lambda f: (f.location.x, f.location.y))

    def run(self, flowers: 'list[Flower]'):
        self.sortFlowers(flowers)
        for i, flower in enumerate(flowers):
            secsToFlower = i / self.flowersPerSec
            millisToFlower = int(round(secsToFlower * 1000))
            pulseTime = self.startTime + millisToFlower
            flower.HuePulse(self.hue, startTime=pulseTime)
            if self.sound:
                flower.PlaySoundFile(self.sound, startTime=pulseTime)
