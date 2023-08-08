from person import Person


class SimpleTracker:
    def __init__(self, bborpoint='bbox'):
        self.counter = 0

    def track(self, frame, detections, conf, hudframe, personTracker):
        print(detections)

        # wipe out existing personTracker
        personTracker = {}
        for bb in detections:
            personTracker[self.counter] = Person(pid=self.counter,bb=bb)
            personTracker[self.counter].draw(hudframe)
            self.counter += 1

            if self.counter == 1000:
                self.counter = 0

        return hudframe

