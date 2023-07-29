from dataclasses import dataclass
import json
import time

import paho.mqtt.client as mqtt


# A person in the field.
@dataclass
class Person():
    name: str = ""
    x: int = None
    y: int = None
    last_seen: int = None

class People():
    def __init__(self):
        self.people = {}
        self.last_update = None

    def updateFromMQTT(self, mqtt_people_update: mqtt.MQTTMessage):
        people_update_json = mqtt_people_update.payload.decode('utf-8')
        update = json.loads(people_update_json)
        
        # Skip received-out-of-order (obsolete) updates
        if self.last_update and self.last_update > update['timestamp']:
            return
        else:
            self.last_update = update['timestamp']

        # Any people *not* included in this update message will be preserved
        # at their prior location.  
        for name, location in update['people'].items():
            if name in self.people:
                person = self.people[name]
            else:
                # We've never seen this person before; instantiate them.
                person = Person(name)
            person.x = location['x']
            person.y = location['y']
            person.last_seen = update['timestamp']

    def removePeopleNotSeenForAWhile(self):
        # How much time can pass without seeing a person before they are 
        # considered gone. During the time between when we stop seeing them and
        # they timeout via this mechanism, the games will treat them as stationary
        # in their last known location.
        PERSON_TIMEOUT = 2000  # milliseconds

        # Timestamps in people updates are milliseconds since the unix epoch
        # (in the mock-people code they come from Javascript's Date.now()), so
        # they are comparable with python's time.time().
        now = time.time()
        for person in list(self.people.keys()):
            time_since_last_seen = now - person.last_seen
            if time_since_last_seen > PERSON_TIMEOUT:
                del self.people[person]
