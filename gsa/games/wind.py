import random
import time

from . import game
from .color_waves import CircularSatValWave
from ..game_state import GameState
from ..geometry import Point

class Wind(game.StatefulGame):
    def __init__(self):
        # Constants controlling the frequency of wind waves
        self.waveGapSecsMean: float = 1.0
        self.waveGapSecsStDev: float = 0.3
        self.waveGapSecsMinimum: float = 0.5
        # State variables
        self.nextWaveTime: int = 0

    def runLoop(self, gameState: GameState):
        now = time.time()
        if now > self.nextWaveTime:
            wave = CircularSatValWave(
                # Start in the future, to give time for communication to full field.
                startTime=gameState.controlTimer() + 5000,
                # Start somewhere randomly on the left edge of the field
                center=Point(x=0, y=random.randint(0, gameState.field.height)),
                startRadius=100,
                # Not all the same speed, but within a narrow range.
                speed=random.randint(350,500),
                # Thes are the parameters that currently give a slight greying/diming
                # TODO: change these once SatValPulse is debugged in the flower firmware
                satChange=0.7,
                valChange=1.0
            )
            wave.run(gameState.flowers)

            delay = random.normalvariate(self.waveGapSecsMean, self.waveGapSecsStDev)
            delay = max(delay, self.waveGapSecsMinimum)
            self.nextWaveTime = now + delay
