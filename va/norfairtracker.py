# Note: for ease of reproducibility, we provide Dockerfiles for all the demos.
# Even though Norfair does not need a GPU, the default configuration of most demos requires a GPU
# to be able to run the detectors.
#
# For this, make sure you install NVIDIA Container Toolkit so that your GPU can be shared with Docker.

from norfair import Detection, Tracker, Video, draw_tracked_objects

class NorfairTracker:
    def __init__(self, bg_subtractor, frame_width, frame_height):
        pass


    def track(self, frame, personTracker, hudframe, medianFrame):
        pass
