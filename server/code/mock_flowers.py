import json
import time
import random
import string
import paho.mqtt.client as mqtt
import sys

from preconfig import PreConfig

pc = PreConfig()

broker_address = '127.0.0.1'
broker_port = 1883
topic = 'flower-heartbeats/'


if len(sys.argv) > 1:
    flowerCount = int(sys.argv[1])
else:
    flowerCount = 1

def get_fid(id):
    return list(pc.inventory)[int(id)]

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

    while True:
        for client in clients:
            flower_id = get_fid(client.id)
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