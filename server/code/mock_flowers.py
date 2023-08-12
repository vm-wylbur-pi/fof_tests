import json
import time
import random
import string
import paho.mqtt.client as mqtt
import sys
import yaml

broker_address = '192.168.1.144'
broker_port = 1883
topic = 'flower-heartbeats/'
DEPLOYMENT_PATH = '../../fake_field/dress_rehearsal_deployment.yaml'


if len(sys.argv) > 1:
    flowerCount = int(sys.argv[1])
else:
    flowerCount = 130

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
    # Create MQTT clients
    clients = []
    for i in range(flowerCount):
        client = mqtt.Client(f'client{i+1}')
        client.id = str(i)
        client.on_connect = on_connect
        client.on_publish = on_publish
        clients.append(client)

    # Connect and start publishing
    for client in clients:
        client.connect(broker_address, broker_port)
        client.loop_start()

    deployment = get_deployment()

    while True:
        for client in clients:
            flower_id = get_fid(deployment, client.id)
            payload = json.dumps({
                'flower_id': flower_id,
                'uptime': 1,
                'IP': '127.0.0.1',
                'wifi_signal': "great",
                'sd_card': 10,
                'volume': 10,
                'ntp_time': int(time.time()),
                'control_timer': 10,
                'FastLED_fps': 10
            })
            res = client.publish(topic, payload)
            print(f'Published: {payload}')
            print(f'Return Code: {res.rc}')
        time.sleep(1)

if __name__ == '__main__':
    main()
