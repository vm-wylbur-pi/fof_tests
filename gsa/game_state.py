import json
import time
from typing import List

import flower
import field
from geometry import Point
import person
import util

class GameState:

    MAX_SECS_BETWEEN_HEARTBEATS = 5.0  # seconds
    MQTT_TOPIC_FOR_HEARTBEATS = "gsa-heartbeats"

    def __init__(self, deployment_file):
        self.flowers: List[flower.Flower] = flower.readFlowersFromDeploymentYAML(deployment_file)
        self.field: field.Field = field.Field(deployment_file)
        self.people: person.People = person.People()
        self.stateful_games = []
        self.control_timer_reference_time: int = None  # seconds since the epoch
        self.mqttThrottler = None  # will be initializedy by MQTT setup
        self.lastHeartbeatTime: float = 0  # In seconds, as returned by time.time()

    # Returns the number of milliseconds that have passed since the 
    # globally shared event reference time.
    def controlTimer(self) -> int:
        if self.control_timer_reference_time is None:
            return None
        nowSecs = time.time()
        timeSinceReferenceSecs = nowSecs - self.control_timer_reference_time
        timeSinceReferenceMillis = timeSinceReferenceSecs * 1000
        return int(round(timeSinceReferenceMillis))

    def runStatelessGame(self, game):
        game.run(self)

    def runStatefulGame(self, game):
        self.stateful_games.append(game)
        self.sendHeartbeat()

    def clearStatefulGames(self, excluded=None):
        [g.stop(self) for g in self.stateful_games if g != excluded]
        self.stateful_games = [] if excluded is None else [excluded]
        self.sendHeartbeat()

    def updateStatefulGames(self):
        # Handle uloading of finished games
        if any(g.isDone() for g in self.stateful_games):
            [g.stop(self) for g in self.stateful_games if g.isDone()]
            self.stateful_games = [g for g in self.stateful_games if not g.isDone()]
            self.sendHeartbeat()

        # Run the main loop for all active games.
        for game in self.stateful_games:
            game.runLoop(self)

    # Broadcast a heartbeat. This is consumed by flower-control interfaces (FCC and DoJ)
    # to give the operator feedback about what's happening, and to confirm that the GSA
    # is running.
    #
    # This is called every time the set of stateful games changes, or every
    # MAX_MAX_SECS_BETWEEN_HEARTBEATS seconds, if no changes have happend in that long.
    def sendHeartbeat(self):
        heartbeatData = {
            "games": [g.__class__.__name__ for g in self.stateful_games],
            "control_timer": self.controlTimer(),
            'IP': util.getIPAddress(),
            'num_people': len(self.people.people),
        }
        heartbeatJson = json.dumps(heartbeatData)
        self.mqttThrottler.sendMessage(topic=GameState.MQTT_TOPIC_FOR_HEARTBEATS,
                                       payload=heartbeatJson)
        self.lastHeartbeatTime = time.time()

    def sendHeartbeatIfItsTime(self) -> str:
        if time.time() - self.lastHeartbeatTime > GameState.MAX_SECS_BETWEEN_HEARTBEATS:
            self.sendHeartbeat()

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

    def closestFlowerTo(self, point: Point) -> flower.Flower:
        flowersByDistance = sorted(self.flowers, key=lambda f: point.distanceTo(f.location))
        return flowersByDistance[0]
