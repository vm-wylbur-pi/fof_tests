from person import Person

# Super simple tracker that assigns new ids to every person on every frame
#  resets ids after 1000 to avoid growing forever

class SimpleTracker:
    def __init__(self, bborpoint='bbox'):
        self.counter = 0

    def track(self, frame, detections, conf, hudframe, personTracker):

        # wipe out existing personTracker
        personTracker.clear()
        for bb in detections:
            bbarray = [bb[0],bb[1],bb[2],bb[3]]
            personTracker[self.counter] = Person(pid=self.counter,bb=bbarray)
            personTracker[self.counter].draw(hudframe)
            self.counter += 1

            if self.counter == 1000:
                self.counter = 0

        return hudframe

