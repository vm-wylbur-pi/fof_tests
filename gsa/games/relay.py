from dataclasses import dataclass
import random

from .game import StatelessGame
from ..game_state import GameState

@dataclass
class RelayCommandToAllFlowers(StatelessGame):
    command: str
    rawParams: str = ""

    def run(self, gameState: GameState):
        print(f"Relaying command to all flowers: {self.command}({self.rawParams})")
        for flower in gameState.flowers:
            flower.sendMQTTCommand(self.command, self.rawParams)
