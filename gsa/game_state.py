import time

import flower
import field
import person

class GameState:
    def __init__(self, deployment_file):
        self.flowers = flower.readFlowersFromDeploymentYAML(deployment_file)
        self.field = field.Field(deployment_file)
        self.people = person.People()
        self.stateful_games = []
        self.control_timer_reference_time: int = None  # seconds since the epoch

    # Returns the number of milliseconds that have passed since the 
    # globally shared event reference time.
    def controlTimer(self) -> int:
        print(f"reference time is {self.control_timer_reference_time}")
        nowSecs = int(round(time.time()))
        timeSinceReferenceSecs = nowSecs - self.control_timer_reference_time
        timeSinceReferenceMillis = timeSinceReferenceSecs * 1000
        return timeSinceReferenceMillis

    def runStatelessGame(self, game):
        game.run(self.flowers)

    def runStatefulGame(self, game):
        self.stateful_games.append(game)

    def clearStatefulGames(self):
        for game in self.stateful_games:
            game.stop(self)
        self.stateful_games = []

    def updateStatefulGames(self):
        self.stateful_games = [g for g in self.stateful_games if not g.isDone()]
        for game in self.stateful_games:
            game.runLoop(self)

    # The start time for games can be specified as an absolute control time in millis,
    # or, more commonly, as an offset relative to the current control timer. This
    # method handles both, returning the absolute start time in either case.
    #   startTimeParametr == "22335"   run when the control timer is 22335
    #   startTimeParameter == "+4000"  run four seconds in the future
    def parseStartTime(self, startTimeParameter: str) -> int:
        if startTimeParameter.startswith("+"):
            offset = int(startTimeParameter[1:])
            print(f"Parsing start-time parameter of {startTimeParameter} into {self.controlTimer() + offset}")
            return self.controlTimer() + offset
        else:
            return int(startTimeParameter)
