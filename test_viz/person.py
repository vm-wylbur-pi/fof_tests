import json
import numpy as np
import cv2
import time
from collections import deque

class Person:
    MAXQUEUE = 100

    def __init__(self, pid, bb):
        self.pid = pid
        self.firstseen = self.lastseen = time.time()
        self.bb = bb
        self.bbQueue = deque(maxlen=self.MAXQUEUE)
        self.pos = [bb[0] + bb[2] // 2, bb[1] + bb[3]]
        self.posQueue = deque(maxlen=self.MAXQUEUE)
        self.dir = None

    def update(self, newbb):
        self.lastseen = time.time()
        self.bbQueue.append(self.bb)
        self.bb = newbb
        self.posQueue.append(self.pos)
        # TODO:  smooth out by averaging over the last X positions
        self.pos = [newbb[0] + newbb[2] // 2, newbb[1] + newbb[3]]
        self.dir = self.direction()

    def direction(self):
        if len(self.posQueue) < 2:
            return None
        mean_start = np.mean([point[0] for point in self.posQueue]), np.mean([point[1] for point in self.posQueue])
        mean_end = np.mean([point[0] for point in self.posQueue]), np.mean([point[1] for point in self.posQueue])
        return [mean_start, mean_end]

    def draw(self, frame):
        # Draw bounding box
        p1 = (int(self.bb[0]), int(self.bb[1]))
        p2 = (int(self.bb[0] + self.bb[2]), int(self.bb[1] + self.bb[3]))
        cv2.rectangle(frame, p1, p2, (0,255,0), 2)

        # Place small red dot at the position
        cv2.circle(frame, (int(self.pos[0]), int(self.pos[1])), 2, (0,0,255), -1)

        # Write pid above the bounding box
        cv2.putText(frame, 'PID: {}'.format(self.pid), (p1[0], p1[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

        # Write position underneath the red dot
        cv2.putText(frame, 'Pos: {}'.format(self.pos), (self.pos[0], self.pos[1] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

        # Write bounding box height and width to the left of the bounding box separated by a comma
        cv2.putText(frame, 'BB: {},{}'.format(self.bb[2], self.bb[3]), (p1[0] - 100, p1[1] + self.bb[3]//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

        return frame

    def write(self):
        person_dict = {
            'pid': self.pid,
            'firstseen': self.firstseen,
            'lastseen': self.lastseen,
            'bb': list(self.bb),
            'bbQueue': list(self.bbQueue),
            'pos': self.pos,
            'posQueue': list(self.posQueue),
            'dir': self.dir,
            'MAXQUEUE': self.MAXQUEUE
        }
        return json.dumps(person_dict)

    @staticmethod
    def read(json_string):
        person_dict = json.loads(json_string)
        new_person = Person(person_dict['pid'], person_dict['bb'])
        new_person.firstseen = person_dict['firstseen']
        new_person.lastseen = person_dict['lastseen']
        new_person.bbQueue = deque(person_dict['bbQueue'], maxlen=new_person.MAXQUEUE)
        new_person.pos = person_dict['pos']
        new_person.posQueue = deque(person_dict['posQueue'], maxlen=new_person.MAXQUEUE)
        new_person.dir = person_dict['dir']
        return new_person
