from dataclasses import dataclass

from .game import StatelessGame
from ..game_state import GameState

@dataclass
class RunningLight(StatelessGame):
    startTime: int
    flowersPerSec: float = 15
    hue: int = 0
    sound: str = None

    def sortFlowers(self, gameState: GameState):
        # This part could be more interesting, if we sorted the flowers
        # in other ways.  (Maybe subclasses?)
        gameState.flowers.sort(key=lambda f: (f.location.x, f.location.y))

    def run(self, gameState: GameState):
        self.sortFlowers(gameState.flowers)
        for i, flower in enumerate(gameState.flowers):
            secsToFlower = i / self.flowersPerSec
            millisToFlower = int(round(secsToFlower * 1000))
            pulseTime = self.startTime + millisToFlower
            flower.HuePulse(self.hue, startTime=pulseTime)
            if self.sound:
                flower.PlaySoundFile(self.sound, startTime=pulseTime)
