import psutil
import unittest
import requests
import json
from collections import OrderedDict

# redis tests
import redis
import traceback

def addResult(suite, test, status, response):
    state_report.append({'suite':suite,'test': test, 'status': status, 'response': response})

class fccTestCases(unittest.TestCase):
    fccURL = "http://127.0.0.1:8000"
    def test_1_fcc_process_running(self):
        process_running = False
        test_result = "Could not detect process for /usr/local/bin/python3 /app/code/fcc.py"

        for process in psutil.process_iter(['status']):
            if process.cmdline() == ['/usr/local/bin/python3', '/app/code/fcc.py'] and process.info['status'] in ['sleeping', 'running']:
                test_result = "Found the fcc python process as expected, it's state was '%s' ...yay!" % process.info['status']
                process_running = True
                break

        addResult('fcc','Python process running', process_running, test_result)

        self.assertTrue(process_running, test_result)

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

class redisTestCases(unittest.TestCase):
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


if __name__ == '__main__':
    global state_report
    state_report = []
    unittest.main(exit=False, verbosity=2)
    print(json.dumps(state_report))

