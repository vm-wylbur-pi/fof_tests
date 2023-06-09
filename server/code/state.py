import psutil
import unittest
import requests
import json
import time
import paho.mqtt.client as mqtt
from collections import OrderedDict

# redis tests
import redis
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
        'mosquitto': {
            'name': ['mosquitto', '-c', 'config/mosquitto.conf'],
            'state': ['sleeping','running']
        },
        'chrony': {
            'name': ['chronyd', '-f', '/etc/chrony/chrony.conf'],
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
            test_result = "Could not detect process --> %s" %pname

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

class c_redisTestCases(unittest.TestCase):
    redisHost = "redis"
    redisPort = 6379
    suite = 'redis'
    rc = None

    rcCommon = ['config','deployment','flowers']

    @classmethod
    def setUpClass(cls):
        cls.rc = redis.Redis(host=cls.redisHost, port=cls.redisPort)

    def test_1_redis_ping(self):
        # Make a GET request to the web server
        response = None
        try:
            response = self.rc.ping()
            if response:
                test_result = "Pinged the redis host '%s' on port '%d'" % (self.redisHost, self.redisPort)
            else:
                test_result = "Ping failed to the redis host '%s' on port '%d'" % (self.redisHost, self.redisPort)
        except Exception as e:
            test_result = "Ping threw an exception: %s" % (str(e))

        addResult(self.suite, 'Redis Ping', response, test_result)
        self.assertTrue(response)

    def test_2_redis_values(self):
        # Make a GET request to the web server
        response = None
        overallResult = True
        for cv in self.rcCommon:
            result = True
            try:
                response = self.rc.get(cv)
                if response:
                    test_result = "%s is available and has %d total" % (cv, len(json.loads(response)))
                else:
                    test_result = "%s list is MISSING??!?!?!" % cv
                    result = False
                    overallResult = False
            except Exception as e:
                test_result = "GET calls threw an exception: %s" % (str(e))

            addResult(self.suite, 'Redis Get %s' % cv, result, test_result)

        self.assertTrue(overallResult)


class d_mosquittoTestCases(unittest.TestCase):
    suite = 'mosquitto'
    broker_address = '127.0.0.1'
    broker_port = 1883
    topic = 'flower-heartbeats/'

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
        test_result = "Could not connect to mosquitto broker on %s port %d" %(self.broker_address, self.broker_port)


        test_result = "Connected to mosquitto broker on %s port %d" %(self.broker_address, self.broker_port)

        addResult(self.suite,'Broker connected', RESULT_TRACKER['MQTT Connect'], test_result)
        self.assertTrue(self.client, RESULT_TRACKER['MQTT Connect'])

# MQTT connect function that blows up if i put it insidet the test class
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        setResult('MQTT Connect', True)
        pass
        # Perform additional actions upon successful connection
    else:
        setResult('MQTT Connect', False)
        raise Execption('could not connect to mosquitto broker')

if __name__ == '__main__':
    global state_report
    state_report = []
    unittest.main(exit=False, verbosity=2)
    print(json.dumps(state_report))

