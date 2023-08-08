import os.path
import paho.mqtt.client as paho_mqtt
import time
import yaml

import geometry
import color

# encapsulates 
#   - What the GSA knows about the flower state, including its location
#   - How to send commands to this flower over MQTT
class Flower:
    def __init__(self, id: str, location: geometry.Point, mqtt_client: paho_mqtt.Client):
        self.id: str = id
        self.location: geometry.Point = location
        self.mqtt_client: paho_mqtt.Client = mqtt_client

        # State used to buffer mqtt commands
        #
        self.currentBlossomColor = None
        # Used to periodically sync the field state with the state the GSA believes
        # it should be.
        self.timeOfColorUpdate = 0
        self.MAX_AGE_OF_COLOR_UPDATE = 20  # seconds

    def sendMQTTCommand(self, command: str, params: str, retained: bool = False):
        topic = f"flower-control/{self.id}/{command}"
        self.mqtt_client.publish(topic, payload=params, retain=retained)

    # Setting n = 1 returns the closest flower to self.
    def findNClosestFlowers(self, flowers, n):
        others = [f for f in flowers if f is not self]
        others.sort(key=lambda f: f.location.diff(self.location).magnitude())
        max_index = min(n, len(flowers))  # Can't return more neighbors than there are other flowers.
        n_closest = others[:max_index]
        print(f"{n} closest flowers to {self.id} are {[f.id for f in n_closest]}")
        return n_closest

    def PlaySoundFile(self, filename, startTime):
        # print(f"{self.id} playing sound file {filename}")
        params = ",".join([filename, startTime])
        self.sendMQTTCommand(command="audio/playSoundFile", params=params)

    def HuePulse(self, hue, startTime, rampDuration, peakDuration, brightness):
        params = f"{hue},{startTime},{rampDuration},{peakDuration},{brightness}"
        self.sendMQTTCommand(command="leds/addPattern/HuePulse", params=params)

    def SetBlossomColor(self, c: color.HSVAColor):
        # To avoid sending a color to every flower on every frame, we only send an
        # update if the flower color changes.  TODO(..only if it changes by a lot. Some
        # changes will be small changes in alpha only.)
        # HSVA are all on the 0-255 scale.
        if (self.currentBlossomColor != c or
            time.time() - self.timeOfColorUpdate > self.MAX_AGE_OF_COLOR_UPDATE):
            #print(f"Updating color for {self.id}, old={self.currentBlossomColor}, new={c}")
            params = f"{c.hue},{c.sat},{c.val},{c.alpha}"
            self.sendMQTTCommand(command="leds/updatePattern/BlossomColor", params=params)
            self.currentBlossomColor = c
            self.timeOfColorUpdate = time.time()


    def FairyVisit(self, visitDuration):
        params = str(visitDuration)
        self.sendMQTTCommand(command="leds/addPattern/FairyVisit", params=params)

    def SetScreenText(self, text):
        self.sendMQTTCommand(command="screen/setText", params=text)


def readFlowersFromDeploymentYAML(yaml_file_name):
    flowers = []
    yaml_file_path = os.path.join(os.path.dirname(__file__), yaml_file_name)
    with open(yaml_file_path, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
        for flower_id, flower in config['flowers'].items():
            flowers.append(Flower(id=flower_id,
                                  location=geometry.Point(flower['x'], flower['y']),
                                  mqtt_client=None))
    print(f"Read {len(flowers)} flowers from {yaml_file_path}")
    return flowers
