import psutil
import unittest
import requests
import json
import time
import paho.mqtt.client as mqtt
from collections import OrderedDict
import sys

#chronyd
import ntplib
from datetime import datetime

# redis tests
import traceback

RESULT_TRACKER = {}

def addResult(suite, test, status, response):
    state_report.append({'suite':suite,'test': test, 'status': status, 'response': response})

# helper function to track state
def setResult(key, val):
    RESULT_TRACKER[key] = val

class a_localProcessTestCases(unittest.TestCase):
    process_list = {
        'fcc': {
            'name': ['/usr/local/bin/python3', '/app/code/fcc.py'],
            'state': ['sleeping', 'running']
        },
        'gsa': {
            'name': ['python3', 'code/fcc.py'],
            'state': ['sleeping', 'running']
        },
        'mosquitto': {
            'name': ['mosquitto', '-c', 'config/mosquitto.conf'],
            'state': ['sleeping','running']
        },
        'chrony': {
            'name': ['chronyd', '-x', '-n', '-f', '/etc/chrony/chrony.conf'],
            'state': ['sleeping','running']
        }
    }

    suite = "local processes"

    def test_1_local_processes_running(self):
        pSuccess = True
        test_result = "Local process checks"
        for pname in self.process_list:
            p = self.process_list[pname]

            process_running = False
            test_result = "Could not detect one of the processes --> "

            for process in psutil.process_iter(['status']):
                if process.cmdline() == p['name'] and process.info['status'] in p['state']:
                    test_result = "Found the %s process as expected, it's state was '%s' ...yay!" % (pname, process.info['status'])
                    process_running = True
                    break

            if not process_running:
                pSuccess = False
                test_result = test_result + " " + pname

            addResult(self.suite,'%s process' % pname, process_running, test_result)

        self.assertTrue(pSuccess, test_result)

class b_fccTestCases(unittest.TestCase):
    fccURL = "http://127.0.0.1:8000"

    def test_2_url_status_code(self):
        test_result = "Could not connect to web server on %s" % self.fccURL
        response = requests.get(self.fccURL)

        res = response.status_code == 200

        if res:
            test_result = "Connected to the web server and got a 200 on %s" % self.fccURL

        addResult('fcc', 'Web Server Accessible', res, test_result)
        self.assertEqual(response.status_code, 200)

    def test_3_http_index(self):
        # Make a GET request to the web server
        response = requests.get(self.fccURL)

        # Check if the expected text is present in the response content
        expected_text = "Flower Control Center"
        res = expected_text in response.text
        if res:
            test_result = "Found '%s' in index.html returned at /" % expected_text
        else:
            test_result = "Couldn't find '%s' in index.html, is the website working?" % expected_text


        addResult('fcc', 'index.html is working', res, test_result)
        self.assertIn(expected_text, response.text)

class d_mosquittoTestCases(unittest.TestCase):
    suite = 'mosquitto'
    broker_address = '127.0.0.1'
    broker_port = 1883
    heartbeats = 'flower-heartbeats/'
    debug_topic = 'state-debug/'

    @classmethod
    def setUpClass(cls):
        cls.client = mqtt.Client('state')
        cls.client.on_connect = on_connect
        cls.client.connect(cls.broker_address, cls.broker_port)
        cls.client.loop_start()
        time.sleep(1)

    def tearDown(self):
        self.client.disconnect()

    def test_1_mosquitto_accessible(self):
        if RESULT_TRACKER['MQTT Connect']:
            test_result = "Connected to mosquitto broker on %s port %d" %(self.broker_address, self.broker_port)
        else:
            test_result = "Could not connect to mosquitto broker on %s port %d" %(self.broker_address, self.broker_port)

        addResult(self.suite,'Broker connected', RESULT_TRACKER['MQTT Connect'], test_result)
        self.assertTrue(self.client, RESULT_TRACKER['MQTT Connect'])

    def test_2_mosquitto_publish(self):
        rt = 'MQTT Topic: %s' % self.debug_topic
        client = mqtt.Client('mqtt-pubish-test')
        client.on_connect = on_connect
        client.connect(self.broker_address, self.broker_port)
        client.subscribe(self.debug_topic)
        client.on_message = on_message
        client.loop_start()
        client.publish(self.debug_topic, 'state check:  testing testing 1 2 3')
        time.sleep(4)

        if rt in RESULT_TRACKER and RESULT_TRACKER[rt]:
            test_result = "Published message to broker on topic %s" % self.debug_topic
            test_end = True
        else:
            test_result = "Could not detect debug message after 2 seconds...although this intermittently fails and i haven't bothered to fix it omg async processes r hard"
            test_end = False

        addResult(self.suite,'Pub/Sub Check', test_end, test_result)
        self.assertTrue(test_end)

    '''def test_3_mosquitto_topics(self):
        rt = 'MQTT Topic: %s' % self.heartbeats
        client = mqtt.Client('mqtt-topic-test')
        client.on_connect = on_connect
        client.connect(self.broker_address, self.broker_port)
        client.subscribe(self.heartbeats)
        client.on_message = on_message
        client.loop_start()
        time.sleep(2)

        if rt in RESULT_TRACKER and RESULT_TRACKER[rt]:
            test_result = "Heard flower-heartbeat messages"
            test_end = True
        else:
            test_result = "Could not detect flower-heartbeats after 2 seconds"
            test_end = False

        client.disconnect()

        addResult(self.suite,'Heartbeat Check', test_end, test_result)
        self.assertTrue(test_end)
'''

class d_chronydTestCases(unittest.TestCase):
    suite = 'ntp'
    server = '127.0.0.1'

    def test_1_ntp_checks(self):

        # Create an NTP client
        client = ntplib.NTPClient()

        ntp_time = None
        try:
            # Request the time from the NTP server
            response = client.request(self.server)
            # Get the NTP server's timestamp
            ntp_time = datetime.fromtimestamp(response.tx_time)

            test_result = "Time check worked, evidently it's %s " % ntp_time
            test_end = True
        except Exception as e:
            test_result = "time check fail for ntp server at %s  ntp time returned: %s" % (self.server, str(e))
            test_end = False

        addResult(self.suite,'Time Check', test_end, test_result)
        self.assertTrue(test_end)


# MQTT connect function that blows up if I put it inside the test class
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        setResult('MQTT Connect', True)
        pass
        # Perform additional actions upon successful connection
    else:
        setResult('MQTT Connect', False)
        raise Exception('could not connect to mosquitto broker')

def on_message(client, userdata, message):
    setResult('MQTT Topic: %s' % message.topic, True)

def on_publish(client, userdata, mid):
    setResult('MQTT Publish', True)

if __name__ == '__main__':
    global state_report
    state_report = []
    unittest.main(exit=False, verbosity=2)
    print(json.dumps(state_report))

