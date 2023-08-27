from dataclasses import dataclass
import random
import time
from typing import List


from .game import StatefulGame, StatelessGame
from ..game_state import GameState
from .color_waves import RandomWaves
from .wave import Wave
from .chorus_circle import ChorusCircle

# If true, all durations are cut by a factor of 50
CYCLE_FAST_FOR_TESTING = True

@dataclass
class IdlePhase:
    gameClasses: List[StatefulGame]  # What to do
    duration: float     # How long to do it, in minutes

idlePhases = (
    IdlePhase(
        [RandomWaves], 1
    ),
    IdlePhase(
        [Wave], 1
    ),
    IdlePhase(
        [ChorusCircle], 2
    ),
)

@dataclass
class FieldIdle(StatefulGame):
    nextPhaseTime: int = 0  # seconds
    nextPhaseIndex: int = 0

    def runLoop(self, gameState: GameState):
        now = time.time()
        if now > self.nextPhaseTime:
            gameState.clearStatefulGames(excluded=self)
            phase = idlePhases[self.nextPhaseIndex]
            for gameClass in phase.gameClasses:
                gameName = gameClass.__name__
                if issubclass(gameClass, StatelessGame):
                    gameState.runStatelessGame(gameClass())
                elif issubclass(gameClass, StatefulGame):
                    gameState.runStatefulGame(gameClass())
                else:
                    print(f"Unexpected class in idle phase: {gameName}")

            phaseDurationSecs = phase.duration * 60
            if CYCLE_FAST_FOR_TESTING:
                phaseDurationSecs /= 50
            
            self.nextPhaseTime = now + (phaseDurationSecs)
            self.nextPhaseIndex = (self.nextPhaseIndex + 1) % len(idlePhases)
