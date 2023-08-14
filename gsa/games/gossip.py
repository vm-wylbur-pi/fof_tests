import random
import time

from . import game
from ..game_state import GameState

# Every now and then, two flowers somewhere in the field have a short
# gossippy conversation.
class Gossip(game.StatefulGame):
    def __init__(self, gapBetweenGossips: int = 60, volume: float = 3.0):
        # Behavior variables.  Constant for any game instance.
        self.gapBetweenGossips: float = gapBetweenGossips  # Seconds
        self.volume = volume
        self.audioFiles = game.getAudioFiles()['Gossip']
        # State variables
        self.nextGossipTime: float = 0  # seconds since epoch, as returned by time.time()

    def runLoop(self, gameState: GameState):
        now = time.time()
        if now > self.nextGossipTime:
            flowerA = random.choice(gameState.flowers)
            flowerB = flowerA.findNClosestFlowers(gameState.flowers, 1)[0]
            conversation = random.choice(list(self.audioFiles.values()));
            print(f"Starting conversation between flowers {flowerA.num} " +
                  f"and {flowerB.num} using audio {conversation}")
            flowerA.SetVolume(self.volume)
            flowerB.SetVolume(self.volume)
            flowerA.PlaySoundFile(conversation[0], startTime='+0')
            flowerB.PlaySoundFile(conversation[1], startTime='+0')
            self.nextGossipTime = now + self.gapBetweenGossips
