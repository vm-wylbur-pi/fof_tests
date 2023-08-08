# Note: for ease of reproducibility, we provide Dockerfiles for all the demos.
# Even though Norfair does not need a GPU, the default configuration of most demos requires a GPU
# to be able to run the detectors.
#
# For this, make sure you install NVIDIA Container Toolkit so that your GPU can be shared with Docker.
import norfair
from norfair import Detection, Tracker, Video, draw_tracked_objects
import numpy as np
from person import Person


class NorfairTracker:
    def __init__(self, bborpoint='bbox'):
        if bborpoint == 'bbox':
            distance_function = 'iou'

        self.nt = Tracker(
            distance_function=distance_function,
            distance_threshold=0.7,
            detection_threshold=0.1
        )

    def track(self, frame, detections, conf, hudframe, personTracker):
        norfair_detections: List[Detection] = []
        cnt = 0
        for detection in detections:
            bbox = np.array(
                [
                    [detection[0].item(), detection[1].item()],
                    [detection[2].item(), detection[3].item()],
                ]
            )
            scores = np.array(
                [conf[cnt].item(), conf[cnt].item()]
            )

            norfair_detections.append(
                Detection(
                    points=bbox, scores=scores, label='person'
                )
            )
            cnt += 1

        tracked_objects = self.nt.update(detections=norfair_detections)

        ids = []

        for tobj in tracked_objects:
            id = tobj.id
            if id:
                ids.append(id)
                bb = tobj.get_estimate()
                bbarray = [int(bb[0][0]),int(bb[0][1]),int(bb[1][0]),int(bb[1][1])]
                if id in personTracker:
                    personTracker[id].update(bbarray)
                else:
                    personTracker[id] = Person(pid=id,bb=bbarray)

                print(bbarray)
                personTracker[id].draw(hudframe)

        personTrackerKeys = set(personTracker.keys())
        ids_to_remove = personTrackerKeys - set(ids)
        for id in ids_to_remove:
            print("------>gotta whack " + str(id))
            personTracker.pop(id,None)
        norfair.draw_boxes(hudframe, tracked_objects)

        return hudframe

