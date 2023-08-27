from dataclasses import dataclass
import random
import time
from typing import List, Tuple, Dict


from .game import Game, StatefulGame, StatelessGame
from ..game_state import GameState

from .audio import PlaySoundOnMultipleFlowers
from .bouncing_blob import BouncingBlob
from .fairy import FairyMob
from .color_waves import RandomWaves
from .wave import Wave
from .chorus_circle import ChorusCircle
from .relay import RelayCommandToAllFlowers

# If true, all durations are cut by a factor of 50
CYCLE_FAST_FOR_TESTING = False


@dataclass
class GameSpec:
    gameClass: type         # class instead of instance to enable repeated instantiation
    gameParams: Dict = None # Optional, games fall back to the game's default params

@dataclass
class IdlePhase:
    duration: float        # How long to do it, in minutes
    games: List[GameSpec]  # What to do (game and parameters)

idlePhases: Tuple[IdlePhase] = (
    # Field default we know and love. Independent idle with rain, no sound.
    IdlePhase(duration=0.2,
              games=[GameSpec(RelayCommandToAllFlowers,
                              {'command': 'leds/clearPatterns'}),
                     GameSpec(RelayCommandToAllFlowers,
                              {'command': 'leds/addPattern/IndependentIdle'}),
                     GameSpec(RelayCommandToAllFlowers,
                              {'command': 'leds/addPattern/Raindrops', 'rawParams': '6,3'}),
                     ]
    ),
    # Darken the field w/power-down sound.  This is a brief phase.
    IdlePhase(duration=0.1,
              games=[GameSpec(RelayCommandToAllFlowers,
                              {'command': 'leds/clearPatterns'}),
                     GameSpec(PlaySoundOnMultipleFlowers,
                              {'soundFile': 'punctuation/PunctuationDOWN.wav', 'numFlowers': 50}),
                     ]
    ),
    # Start strong, with dark-field mallet-sound waves, for 3 minutes
    IdlePhase(duration=3,
              games=[GameSpec(Wave)]
    ),
    # Chorus circle over rain-only
    IdlePhase(duration=3,
              games=[GameSpec(RelayCommandToAllFlowers,
                              {'command': 'leds/clearPatterns'}),
                     GameSpec(RelayCommandToAllFlowers,
                              {'command': 'leds/addPattern/Raindrops', 'rawParams': '2,3'}), 
                     GameSpec(ChorusCircle),
                    ]
    ),
    # Some bouncing blob, just for one minute
    IdlePhase(duration=1,
              games=[GameSpec(RelayCommandToAllFlowers,
                              {'command': 'leds/clearPatterns'}),
                     GameSpec(BouncingBlob),
                    ]
    ),
    # A growing mob of fairies
    IdlePhase(duration=1,
              games=[GameSpec(RelayCommandToAllFlowers,
                              {'command': 'leds/clearPatterns'}),
                     GameSpec(FairyMob),
                    ]
    ),
    # Dark-field mallet Waves again.  This is a good one
    IdlePhase(duration=3,
              games=[GameSpec(RelayCommandToAllFlowers,
                              {'command': 'leds/clearPatterns'}),
                     GameSpec(Wave),
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
