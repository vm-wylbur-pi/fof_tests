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
    def __init__(self, id: str, num: int,
                 location: geometry.Point, mqttThrottler):
        self.id: str = id
        self.num: int = num
        self.location: geometry.Point = location
        self.mqttThrottler = mqttThrottler

        # State used to buffer mqtt commands
        self.currentBlossomColor: color.HSVAColor = None
        self.currentRaindropFrequency: int = None # Drops per second


    def sendMQTTCommand(self, command: str, params: str, retained: bool = False):
        topic = f"flower-control/{self.id}/{command}"
        self.mqttThrottler.sendMessage(topic, payload=params, retain=retained, qos=0)

    # Setting n = 1 returns the closest flower to self.
    def findNClosestFlowers(self, flowers, n: int):
        others = [f for f in flowers if f is not self]
        others.sort(key=lambda f: f.location.diff(self.location).magnitude())
        max_index = min(n, len(flowers))  # Can't return more neighbors than there are other flowers.
        n_closest = others[:max_index]
        # print(f"{n} closest flowers to {self.id} are {[f.id for f in n_closest]}")
        return n_closest

    def SetVolume(self, volume: float):
        params = f"{volume:.1f}" # Format with one decimal place, e.g. "3.0"
        self.sendMQTTCommand(command="audio/setVolume", params=params)

    def PlaySoundFile(self, filename, startTime="+0"):
        #print(f"{self.id} playing sound file {filename} at {startTime}")
        params = f"{filename},{startTime}"
        self.sendMQTTCommand(command="audio/playSoundFile", params=params)

    def HuePulse(self, hue, startTime="+0", rampDuration=300, peakDuration=200, brightness=250):
        params = f"{hue},{startTime},{rampDuration},{peakDuration},{brightness}"
        self.sendMQTTCommand(command="leds/addPattern/HuePulse", params=params)

    def SatValPulse(self, satChange, valChange, startTime, rampDuration, peakDuration):
        params = f"{satChange},{valChange},{startTime},{rampDuration},{peakDuration}"
        self.sendMQTTCommand(command="leds/addPattern/SatValPulse", params=params)

    def SetBlossomColor(self, col: color.HSVAColor, startTime: str = "+0"):
        # To avoid sending a color to every flower on every frame, we only send an
        # update if the flower color changes.  TODO(..only if it changes by a lot. Some
        # changes will be small changes in alpha only.)
        # HSVA are all on the 0-255 scale.
        if self.currentBlossomColor != col:
            #print(f"Updating color for {self.id}, old={self.currentBlossomColor}, new={col}")
            params = f"{col.hue},{col.sat},{col.val},{col.alpha},{startTime}"
            self.sendMQTTCommand(command="leds/updatePattern/BlossomColor", params=params)
            self.currentBlossomColor = col

    def SetRaindropFrequency(self, freq: int):
        if self.currentRaindropFrequency != freq:
            self.sendMQTTCommand(command="leds/updatePattern/Raindrops", params=str(freq))
            self.currentRaindropFrequency = freq

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
            flowers.append(Flower(id=flower_id, num=int(flower['id']),
                                  location=geometry.Point(flower['x'], flower['y']),
                                  mqttThrottler=None))
    print(f"Read {len(flowers)} flowers from {yaml_file_path}")
    return flowers
