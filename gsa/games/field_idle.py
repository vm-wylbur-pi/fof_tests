from dataclasses import dataclass
import random
import time
from typing import List, Tuple, Dict


from .game import Game, StatefulGame, StatelessGame
from ..game_state import GameState

from .audio import PlaySoundOnMultipleFlowers
from .color_waves import RandomWaves
from .wave import Wave
from .chorus_circle import ChorusCircle
from .relay import RelayCommandToAllFlowers

# If true, all durations are cut by a factor of 50
CYCLE_FAST_FOR_TESTING = True


@dataclass
class GameSpec:
    gameClass: type         # class instead of instance to enable repeated instantiation
    gameParams: Dict = None # Optional, games fall back to the game's default params

@dataclass
class IdlePhase:
    duration: float        # How long to do it, in minutes
    games: List[GameSpec]  # What to do (game and parameters)

idlePhases: Tuple[IdlePhase] = (
    IdlePhase(duration=1,
              games=[GameSpec(RandomWaves)]
    ),
    IdlePhase(duration=1,
              games=[GameSpec(Wave)]
    ),
    IdlePhase(duration=2,
              games=[GameSpec(ChorusCircle,
                     {'gapBetweenSongs': 30, 'volume': 5.0}),
        ]
    ),
    # Conclusion: Play the overture while running hue waves over a dark background.
    IdlePhase(duration=7.4,  # the overture is 7.3 minutes long
              games=[GameSpec(RelayCommandToAllFlowers,
                              {'command': 'leds/clearPatterns'}),
                     GameSpec(RelayCommandToAllFlowers,
                              {'command': 'leds/addPattern/Raindrops', 'rawParams': '2,3'}),
                     GameSpec(RandomWaves),
                     GameSpec(RelayCommandToAllFlowers,
                              {'command': 'audio/setVolume', 'rawParams': '5.0'}),
                     GameSpec(PlaySoundOnMultipleFlowers,
                              {'soundFile': 'long-songs/FieldofFlowersOverture.wav', 'numFlowers': 10}),
                    ]
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
            phaseDurationSecs = phase.duration * 60
            if CYCLE_FAST_FOR_TESTING:
                phaseDurationSecs /= 50

            print(f"Starting next idle phase, duration is {phaseDurationSecs} seconds.")

            for spec in phase.games:
                gameName = spec.gameClass.__name__
                print(f"   {gameName}({spec.gameParams})")
                if spec.gameParams is None:
                    gameInstance = spec.gameClass()
                else:
                    gameInstance = spec.gameClass(**spec.gameParams)

                if isinstance(gameInstance, StatelessGame):
                    gameState.runStatelessGame(gameInstance)
                elif isinstance(gameInstance, StatefulGame):
                    gameState.runStatefulGame(gameInstance)
                else:
                    print(f"Unexpected class in idle phase: {gameName}")
            
            self.nextPhaseTime = now + (phaseDurationSecs)
            self.nextPhaseIndex = (self.nextPhaseIndex + 1) % len(idlePhases)
