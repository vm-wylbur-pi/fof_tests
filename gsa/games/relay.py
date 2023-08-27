from dataclasses import dataclass
import random

from .game import StatelessGame
from ..flower import Flower

@dataclass
class RelayCommandToAllFlowers(StatelessGame):
    command: str
    rawParams: str

    def run(self, flowers: 'list[Flower]'):
        print(f"Relaying command to all flowers: {self.command}({self.rawParams})")
        for flower in flowers:
            flower.sendMQTTCommand(self.command, self.rawParams)
