import functools
import os
import yaml

from ..field import Field

class Game:
    # Factory method to construct a randomized instance of a game.
    @classmethod
    def randomInstance(cls, gameState):
        raise NotImplementedError

class StatelessGame(Game):
    def run(self, flowers):
        # Send commands to flowers in order to run this game/effect.
        # This method must not block nor take too long.
        raise NotImplementedError

class StatefulGame(Game):
    # This method is called repeatedly, every time through the main game loop
    def runLoop(self, gameState):
        raise NotImplementedError

    # This method is called once per game loop. When it returns true, the game
    # is stopped, and runLoop will never be called again.
    def isDone(self):
        # Default behavior is to run indefinitely. Unless this
        # method is overridden, the game is only stopped by
        # running game-control/clearGames
        return False
    
    # This method is called to end the game. It gives the game a chance to
    # clean up any external state, such as retained MQTT messages, and/or
    # sending commands to flowers to end indefinitely-running patterns.
    def stop(self, gameState):
        # By default, no cleanup happens.
        pass

# Reads the configuration file containing the set of audio files available to games.
# TODO: make this a class method of Game
@functools.lru_cache
def getAudioFiles():
    # Assumed to be in the same directory as main.py
    AUDIO_CONFIG_YAML_FILE = "../audio_files.yaml"
    yaml_file_path = os.path.join(os.path.dirname(__file__), AUDIO_CONFIG_YAML_FILE)
    with open(yaml_file_path, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)