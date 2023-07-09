import json
import time
import datetime
import random
import string
import paho.mqtt.client as mqtt
import sys
import yaml

broker_address = '127.0.0.1'
broker_port = 1883
topic = 'people-locations/'
DEPLOYMENT_PATH = '/app/fake_field/patricks_backyard_party_deployment.yaml'

class Mob:
    def __init__(self):
        self.list = {}

    def add(self,pid):
        p = Person(pid)
        self.list[pid] = Person(pid)

    def move(self):
        for p in self.list:
            self.list[p].move()
    def dump(self):
        llist = {}
        for p in self.list:
            llist[p] = self.list[p].dump()
        return json.dumps({
            'timestamp': datetime.datetime.now().isoformat(),
            'people': llist
        })

class Person:
    def __init__(self, id):
        self.person_id = id
        self.x = 0
        self.y = 0

    def move(self):
        self.x = self.x +1
        self.y = self.y + 1

    def dump(self):
        return json.dumps({
            'person_id': self.person_id,
            'x': self.x,
            'y': self.y
        })

if len(sys.argv) > 1:
    peopleCount = int(sys.argv[1])
else:
    peopleCount = 1

def get_fid(deployment, id):
    return list(deployment['flowers'])[int(id)]

def get_deployment():
    with open(DEPLOYMENT_PATH, 'r') as file:
        deployment_data = yaml.safe_load(file)
    return deployment_data

def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker')

def on_publish(client, userdata, mid):
    print(f'Message published: {mid}')

def main():
    # Create MQTT client
    client = mqtt.Client(f'mock-people')
    client.id = 'mock-people'
    client.on_connect = on_connect
    client.on_publish = on_publish

    client.connect(broker_address, broker_port)
    client.loop_start()

    deployment = get_deployment()



    m = Mob()
    peeps = [m.add(x) for x in range(peopleCount)]

    while True:
        m.move()
        payload = m.dump()
        res = client.publish(topic, payload)
        time.sleep(0.1)
        print(f'Published: {payload}')
        print(f'Return Code: {res.rc}')

if __name__ == '__main__':
    main()
