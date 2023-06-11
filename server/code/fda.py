import json
import redis
import paho.mqtt.client as mqtt
import time
import sys

from preconfig import PreConfig

pc = PreConfig()
config = pc.config
inventory = pc.inventory
deployment = pc.deployment
rc = pc.rc

# Helper function to purge the queues if something's gone horribly wrong
def flush():
    toflush = []
    toflush.extend(rc.keys(config['redis']['liveflowers'] + '*'))
    toflush.extend(rc.keys(config['redis']['deadflowers'] + '*'))
    for key in toflush:
        rc.delete(key)

# MQTT on_connect event handler
def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    print('Subscribing to heartbeats at: %s' % config['broker']['heartbeats'])
    client.subscribe(config['broker']['heartbeats'])


# MQTT on_message event handler
def on_message(client, userdata, msg):
    heartbeat = json.loads(msg.payload)
    fid = heartbeat['flower_id']
    rfid = config['redis']['liveflowers'] + fid
    rcf = rc.get(rfid)

    lf = None
    if rcf:
        lf = json.loads(rcf)

    # TODO:  handle un-recognized flowers
    if not lf:
        lf = inventory[fid]

    # TODO:  handle non-positioned flowers better than setting to null
    if fid in deployment['flowers']['positions']:
        lf['position'] = deployment['flowers']['positions'][fid]
    else:
        lf['position'] = None

    lf.update(heartbeat)
    lf['last_seen'] = int(time.time())

    rc.set(rfid, json.dumps(lf))

    #purge from dead flowers if it's now alive
    rdfid = config['redis']['deadflowers'] + fid
    if rc.get(rdfid):
        rc.delete(rdfid)


#flush()
#sys.exit()
print("FDA - Starting up")
# Create MQTT client and connect to broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(config['broker']['host'], config['broker']['port'])

# Start the MQTT client loop in the background
client.loop_start()

# Prune out dead flowers
while True:
    time.sleep(pc.HEARTBEAT_TIMEOUT-1)

    lfids = rc.keys(config['redis']['liveflowers'] + '*')
    for lfid in lfids:
        flower = json.loads(rc.get(lfid).decode('utf-8'))
        fid = lfid.decode('utf-8').split(':',1)[1]
        dfid = config['redis']['deadflowers'] + fid
        if int(time.time()) - pc.HEARTBEAT_TIMEOUT > flower['last_seen']:
            rc.set(dfid, json.dumps(flower))
            rc.delete(lfid)

print("FDA - Shutting Down")