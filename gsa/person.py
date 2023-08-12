from dataclasses import dataclass
import json
import random
import time
from typing import Any, List, Callable, Dict

import paho.mqtt.client as mqtt

import geometry
from util import RingBuffer

# A person in the field.
@dataclass
class Person():
    name: str = ""
    location: geometry.Point = None
    last_seen: int = None
    recent_locations: RingBuffer = RingBuffer(capacity=20)  # Two seconds of history at 10 FPS

    def isMoving(self):
        # TODO: This could be better if it took into account timing. We could store the
        #       timestamps of the recent locations and have a speed threshold instead 
        #       of a distance threshold.
        if len(self.recent_locations) < 10:
            # Don't try to decide if people are moving before we have some location history
            return False
        old_location = geometry.AveragePoint(self.recent_locations[:5])
        new_location = geometry.AveragePoint(self.recent_locations[5:])
        dist = old_location.distanceTo(new_location)
        MOVING_DISTANCE_THRESHOLD = 10  # In field units which should be inches.
        # if (dist < MOVING_DISTANCE_THRESHOLD):
        #     print(f"{self.name} is not moving. Old avg: {old_location}, New avg: {new_location}, dist: {dist}")
        return dist > MOVING_DISTANCE_THRESHOLD
        

class People():
    def __init__(self):
        self.people: Dict[str, Person] = {}
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
            person = None
            if name in self.people:
                person = self.people[name]
            else:
                # We've never seen this person before; instantiate them.
                person = Person(name)
                self.people[name] = person
            person.location = geometry.Point(location['x'], location['y'])
            person.recent_locations.add(person.location)
            person.last_seen = int(update['timestamp'])

    def removePeopleNotSeenForAWhile(self):
        # How much time can pass without seeing a person before they are 
        # considered gone. During the time between when we stop seeing them and
        # they timeout via this mechanism, the games will treat them as stationary
        # in their last known location.
        PERSON_TIMEOUT = 2000  # milliseconds

        # Timestamps in people updates are milliseconds since the unix epoch
        # (in the mock-people code they come from Javascript's Date.now()), so
        # they are comparable with python's time.time().
        now = time.time() * 1000
        for name in list(self.people.keys()):
            time_since_last_seen = now - self.people[name].last_seen
            if time_since_last_seen > PERSON_TIMEOUT:
                print(f"Forgetting about {name}, who hasn't been seen in a while.")
                del self.people[name]


# Class to track the association of some set of items (hues, sounds, etc) with 
# each person on the field. Handles the assignment of an item to new people
# when they arrive on the field.  Keeps the same item assigned to the same person,
# even if they disappear for a while then reappear.
class RandomizedAssignments:

    # assignableItems: the values that can be assigned to a person.
    # itemGenerator: If this is provided, it will be called to generate new items
    # after the assignableItems have been exhausted. If not, the assignableItems
    # will be recycled (so that one of them is assigned to more than one person).
    def __init__(self, assignableItems: List[Any], itemGenerator: Callable[[], Any] = None):
        self.asignableItems = assignableItems
        self.itemGenerator = itemGenerator
        # Which person has which item. People are their names.
        self.assignments: dict[str, Any] = {}

    def chooseNextItem(self):
        unassigned_items = [item for item in self.asignableItems
                            if item not in self.assignments.values()]
        if unassigned_items:
            return random.choice(unassigned_items)
        else:
            # The items have all been assigned.  We'll either generate one
            # using the provided function...
            if self.itemGenerator:
                return self.itemGenerator()
            else:
                # ...or pick a random item to re-use among those assigned the least so far.
                use_counts = [self.asignableItems.count(item) for item in self.asignableItems]
                min_use_count = min(use_counts)
                items_used_least = [item for item in self.asignableItems
                                    if list.count(item) == min_use_count]
                return random.choice(items_used_least)

    def updateAssignments(self, activePersonNames):
        assignedNames = list(self.assignments.keys())
        for name in assignedNames:
            if name not in activePersonNames:
                del self.assignments[name]
                print(f"Removed assignment from {name}.")

        for name in activePersonNames:
            if name not in self.assignments:
                self.assignments[name] = self.chooseNextItem()
                print(f"Assigned {self.assignments[name]} to {name}.")

    def getAssignment(self, name: str) -> Any:
        if name not in self.assignments:
            print("WARNING: Requested assignment of unknown person, assigning new item.")
            self.assignments[name] = self.chooseNextItem()
        return self.assignments.get(name, None)
