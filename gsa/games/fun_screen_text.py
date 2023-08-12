from dataclasses import dataclass
import random
import textwrap
import time
import os

from . import game
from ..game_state import GameState

@dataclass
class FunScreenText(game.StatefulGame):
    # How long between text changes on each individual flower.
    per_flower_change_interval_secs = 3 * 60

    def __init__(self):
        self.first_run = True
        self.nextFlowerIdx = 0
        self.nextChangeTime = 0
        self.readMessagesFromDataFile()
        self.msgGenerator = self.makeMessageGenerator()

    def readMessagesFromDataFile(self):
        # This is hard-coded for now, no real reason not to...
        msg_filename = "../fun_screen_messages.txt"
        msg_path = os.path.join(os.path.dirname(__file__), msg_filename)
        self.messages = []
        with open(msg_path, 'r') as msg_lines:
            for line in msg_lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # If we change the font size on the screen, this width should change too.
                    wrapped_msg = '\n'.join(textwrap.wrap(line, width=9))
                    self.messages.append(wrapped_msg)
        print(f'FunScreenText read {len(self.messages)} from {msg_filename}')

    def makeMessageGenerator(self):
        while True:
            random.shuffle(self.messages)
            for message in self.messages:
                yield message

    def runLoop(self, gameState: GameState):
        if not gameState.flowers:
            return
        if self.first_run:
            # Put a message on every flower, before starting to change them.
            for flower in gameState.flowers:
                flower.SetScreenText(next(self.msgGenerator))
            self.first_run = False
        else:
            now = time.time()
            if now > self.nextChangeTime:
                gameState.flowers[self.nextFlowerIdx].SetScreenText(
                    next(self.msgGenerator))
                self.nextFlowerIdx = (self.nextFlowerIdx + 1) % len(gameState.flowers)
                delay = self.per_flower_change_interval_secs / len(gameState.flowers)
                self.nextChangeTime = now + delay

    def stop(self, gameState: GameState):
        # TODO: Add a screen/showFlowerInfo command to each flower, and call
        # it here, to return each flower display to the debug info showing
        # the flower identifiers and firmware build details.
        pass
