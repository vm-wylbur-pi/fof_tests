import os.path
import paho.mqtt.client as paho_mqtt
import yaml

import geometry

# encapsulates 
#   - What the GSA knows about the flower state, including its location
#   - How to send commands to this flower over MQTT
class Flower:
    def __init__(self, id: str, location: geometry.Point, mqtt_client: paho_mqtt.Client):
        self.id = id
        self.location = location
        self.mqtt_client = mqtt_client

    def sendMQTTCommand(self, command: str, params: str):
        topic = f"flower-control/{self.id}/{command}"
        self.mqtt_client.publish(topic, payload=params)

    # Setting n = 1 returns the closest flower to self.
    def findNClosestFlowers(self, flowers, n):
        others = [f for f in flowers if f is not self]
        others.sort(key=lambda f: f.location.diff(self.location).magnitude())
        max_index = min(n, len(flowers))  # Can't return more neighbors than there are other flowers.
        n_closest = others[:max_index]
        print(f"{n} closest flowers to {self.id} are {[f.id for f in n_closest]}")
        return n_closest

    def PlaySoundFile(self, filename):
        # print(f"{self.id} playing sound file {filename}")
        self.sendMQTTCommand(command="audio/playSoundFile", params=filename)

    def HuePulse(self, hue, startTime, rampDuration, peakDuration, brightness):
        params = f"{hue},{startTime},{rampDuration},{peakDuration},{brightness}"
        self.sendMQTTCommand(command="leds/addPattern/HuePulse", params=params)

    def FairyVisit(self, visitDuration):
        params = str(visitDuration)
        self.sendMQTTCommand(command="leds/addPattern/FairyVisit", params=params)


def readFieldFromDeploymentYAML(yaml_file_name):
    field = []
    yaml_file_path = os.path.join(os.path.dirname(__file__), yaml_file_name)
    with open(yaml_file_path, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
        for flower_id, flower in config['flowers'].items():
            field.append(Flower(id=flower_id,
                                location=geometry.Point(flower['x'], flower['y']),
                                mqtt_client=None))
    print(f"Read {len(field)} flowers from {yaml_file_path}")
    return field
