from dataclasses import dataclass
import random
import time

from . import game
from ..game_state import GameState
from ..flower import Flower

# A moving spot of light on a flower, which jumps from flower to flower.
# The game-level logic controls which flower the fairy is on, and for how long.
# The flower-level code controls which part of the flower the fairy lights up,
# the speed of drift within the flower, the number of LEDs lit at a time.
@dataclass
class Fairy(game.StatefulGame):
    def __init__(self):
        # Behavior variables.  Constant for any game instance.
        self.secsPerVisitMean: float = 3.0
        self.secsPerVisitStDev: float = 2.0
        self.secsPerVisitMinimum: float = 0.5
        # Possible extension: add a specified color to the fairy. For now, it's gold.

        # State variables
        self.current_flower: Flower = None
        self.next_visit_time: int = 0

        fairy_audio_files = game.getAudioFiles()['Fairy']
        self.fairyName = random.choice(list(fairy_audio_files.keys()))
        self.giggle_sequence = list(fairy_audio_files[self.fairyName])
        random.shuffle(self.giggle_sequence)
        self.next_giggle_idx = 0

    def nextGiggleFilename(self):
        giggle_filename = self.giggle_sequence[self.next_giggle_idx]
        self.next_giggle_idx += 1
        if self.next_giggle_idx >= len(self.giggle_sequence):
            self.next_giggle_idx = 0
            # Change up the order of giggles for the next time we use each of them.
            random.shuffle(self.giggle_sequence)
        return giggle_filename

    def runLoop(self, gameState: GameState):
        now = time.time()
        if now > self.next_visit_time:
            candidates = (gameState.flowers if self.current_flower is None
                          else self.current_flower.findNClosestFlowers(gameState.flowers, 3))
            next_flower = random.choice(candidates)
            visitDuration = random.normalvariate(
                self.secsPerVisitMean, self.secsPerVisitStDev)
            visitDuration = max(visitDuration, self.secsPerVisitMinimum)
            # Visit duration is expected on the flower in milliseconds
            visitDurationMillis = int(round(visitDuration * 1000))
            next_flower.FairyVisit(visitDurationMillis)
            next_flower.PlaySoundFile(self.nextGiggleFilename())
            self.next_visit_time = now + visitDuration
            self.current_flower = next_flower

    def isDone(self):
        # TODO: we could specify a duration. For now, the only way to end the game
        #       is to clear all games.
        return False
