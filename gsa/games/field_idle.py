from dataclasses import dataclass
import random
import time


from .game import StatefulGame
from ..game_state import GameState
from .color_waves import RandomWaves
from .wave import Wave
from .chorus_circle import ChorusCircle

@dataclass
class FieldAction:
    gameClass: StatefulGame  # What to do
    duration: float     # How long to do it in minutes

fieldActions = (
    FieldAction(RandomWaves, 0.1),
    FieldAction(Wave, 0.1),
    FieldAction(ChorusCircle, 0.1),
)

class FieldIdle(StatefulGame):

    def __init__(self):
        self.nextActonTime: int = 0  # seconds
        self.refillActionList()
    
    def refillActionList(self):
        self.actionList = list(fieldActions)
        random.shuffle(self.actionList)

    def runLoop(self, gameState: GameState):
        now = time.time()
        if now > self.nextActonTime:
            gameState.clearStatefulGames(excluded=self)
            if not self.actionList:
                self.refillActionList()
            action = self.actionList.pop()
            gameName = action.gameClass.__name__
            print(f"Running {gameName} for {action.duration} minutes.")
            gameState.runStatefulGame(action.gameClass())
            self.nextActonTime = now + (action.duration * 60)
