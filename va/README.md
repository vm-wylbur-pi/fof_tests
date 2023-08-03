# Visual Administrator (VA)

Welcome to the VA system which is responsible for taking live images from the USB camera running in IR, calibrating the image to remove distortion, detect people in the frame, tracks individuals, determines their coordinates on the playa, and broadcasts those out over MQTT.


## Installation
The requirements.txt file contains the python libraries needed to operate the VA.  It's best installed in a virtual environment.

```
pip3 -m venv viz
source viz/bin/activate
pip3 install -r va/requirements.txt`
```
The default install is designed to read from a video file for testing.  Video files are not in git, but can be downloaded [here](https://drive.google.com/drive/folders/1f7jRAl51KhkgIn1FLvAdRdgrnfLxoVL_?usp=sharing). Note that the corner detection didn't quite work properly for the test footage due to losing some of the edges to un-distortion so the locations on the field will be slightly off.

Once requirements are installed and downloaded the VA can be run using
```
python3 va.py
```

Variables in the code can enable/disable and configure various features.
* MQTT_BROKER_IP:  exactly what you'd think, defaults to 127.0.0.1
* CHANNEL:  Video file you want to read from or integer number of usb camera
* MAX_FRAMES:  Runs a limited number of frames from the video, useful for stopping early
* WEBSOCKET:  Open up a small webserver on port 8000 that shows every WEBSOCKET_RATE frames post processing.  Useful for debugging and seeing what the output of the camera and tracking system are.

When running, the va will print out a stream of debug messages with the number of people that it detected in the field and the time it took to process the image.  The people should be visible as grey squares moving around the field - I've been using the Mock People field page to watch them move.


## Under the Hood
The VA pipeline is split into multiple parts.

1) Corner detection
   Designed to take variables from the deployment file to identify the general location of the corners of the field.  This is used in mapping points in the frame to x,y coordinates on the playa.  To deal with movement of the camera due to wind the system will look for bright spots around those points and shift the corner to the center of the bright spot.

2) Frame Calibration / Undistortion
   The cameras used have a fish-eye effect that enable getting more of the field in the frame but must be un-distorted in order to remove warping and return accurate x,y coordinates.  The undistortion process clips out a section of the frame - a surprise to me - which is why the testing video doesn't have accurate corners and people drift around a bit.

3) People Identification
   Done using a pre-trained set of YOLO models that are generated using roboflow (data set creation) and ultralytics hub for training and model generation.  There are several pre-trained models in the va/models directory and I'll be generating more from the training data we have.  The model being used can be adjusted in the ultratracker.py file.

4) Tracking People
   Turns out this is an intense area of research with handful of off-the-shelf implementations available.  The ones currently being used are based on relatively new ByteTrack and BotSort process as implemented by the Ultralytics package.  These trackers are still a work in progress to figure out what combination of settings and model return the most consistent results.  See Current Challenges section next.

5) MQTT Broadcast
   Once people are identified in the frame the list of people / x,y coordinates are broadcast over mqtt to the people-locations/ topic.

6) Debug Web Interface
   In order to see what the camera's seeing on the playa the VA opens a webserver on port 8000 and uses websockets to post periodic frames that are received with bounding boxes added to the viewed frame.  This is also useful in testing to match what the camera is seeing to what's being sent over MQTT.


## Current Challenges
It's been a fair amount of work to get to these points (get it points) and there's still dialing-in to do.

### Throughput - solved by throwing hardware at it.
Real-time person detection in video frames is a processor-intensive operation.  On a relatively modern Macbook Air I can get around 20fps, dropping down to 1fps on the raspberry pi.  The solution to this is to use GPU off-loading, which is really only supported on Nvidia graphics cards.  I've got a laptop with an nvidia card tested that runs as fast as 40fps with periodic slowdowns likely due to other processes on the Windows OS being stupid.

On-playa the plan is to utilize the laptop as the primary VA platform, then fall back to an Intel Nuc that runs around 10fps, followed by the pi which run at 1-2fps if I can't get additional hardware online between now and then.  There are also techniques to hyper-optimize models to run more efficiently on CPUs, not sure if I'm going to get those working before hand.


### Model Accuracy - still traning and trying out different types
Model training / re-training has been worked out using online tooling from Ultralytics Hub that uses Google Collab to run the GPU-intensive training processes.  Ultralytics also makes it possible to spit out models for different versions of YOLO (currently the new hotness in person identification).

I'm still experimenting with different YOLO versions, data sets, and training parameters, and plan to arrive on the playa with a bunch to choose from, but we won't know exactly what works best until we get into the field.  Once we're there I may have the ability to do local training on data we caputure, but that'll depend on whether that's the right use of time between now and then.

Even with the new models I'm still seeing distortions when running footage through where people aren't detected or where their bounding-box is extended to include a flower that they're next to.  Depending on the position of the person, extending the bounding boxes can significantly change the person's point on the field.

I suspect that we'll see more of this when there are more people and more flowers on the field.  We did train the models specifically to detect flowers in addition to people, but they only had a few flowers to choose from and it doesn't seem to be sufficient to train them that a person is not a flower - the models simply return a bounding box around a person + flower combination.

I plan to capture more test footage during the dress rehersal which we could use to do another round of training which includes drawing boxes around people as they move past flowers.

I've also tried out a few background subtraction algorithms from OpenCV as well as a simple background subtraction based on median frames.  Those haven't been wired into the recent YOLO video processing system, but they could help remove the flowers from the frame and reduce overlap - that's an if though considering the flowers will be lighting up which could make them break through the background subtraction processes.


### Tracker Consistency  - still very flaky
The tracking implementations in Ultralytics are flaky and so far tend to not track all the people on the field, will shift identifications between groups, and will stop tracking people but continue broadcasting their last known location.  The end result is better than random assignment, but not nearly as good as it needs to be for an experience on the playa that "JUST WORKS".  So far the IOU variable in the tracker call seems to make the biggest difference in accuracy vs the contents of the bytetrack.yml and botsort.yml files.

In addition to the two trackers built into Ultralytics there's an additional package named Norfair that is desgined to be more configurable and could provide a better experience.  I wired it into the previous models and got it to kick out tracks, but haven't wired it into the new YOLO models.  The implementation supports using points to track people and not just boundingboxes which may be more effective than

I also built a super stupid tracker initially that just naievely relates current points on the field to the nearest previous points on the field.

It turns out tha tpersistent tracking is based on a combination of nearness and prediction algorithms rather than re-processing the images to see if this blob looks like the last blob.  That makes the processing very sensitive to the accuracy of the trackers.
