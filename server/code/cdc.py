import json
import yaml
import redis
import csv
import os

CONFIG_FILE = 'config/default-deployment.yml'
INVENTORY_FILE = 'inventory/flower-inventory.csv'

DEPLOY_DIR = 'deployments/'
DEPLOY_FILE = 'config/default-deployment.yml'

def inventory_to_redis():
    data_dict = {}

    with open(INVENTORY_FILE, 'r') as csvfile:
        reader = csv.reader(csvfile)

        # Skip the first three rows
        for _ in range(3):
            next(reader)

        for row in reader:
            sequence, mac, flower_type = row

            # Create an object with flower_type
            flower_object = {
                'flower_type': flower_type,
                'sequence': sequence
            }

            # Add the object to the dictionary using FoF Mac as the key
            data_dict[mac] = flower_object
    print(data_dict)
    rc.set('flowers',json.dumps(data_dict))


def config_to_redis():
    # Read YAML file
    with open(CONFIG_FILE, 'r') as file:
        config_data = yaml.safe_load(file)

    # Convert YAML to JSON
    json_data = json.dumps(config_data)

    # Store JSON object in Redis
    rc.set('config', json_data)


def deployment_to_redis():
    deploy_val = os.environ.get('FOF_DEPLOYMENT')
    df = DEPLOY_FILE
    if deploy_val is not None:
        df = DEPLOY_DIR + deploy_val + '.yml'

    with open(df, 'r') as file:
        deploy_data = yaml.safe_load(file)

    rc.set('deployment', json.dumps(deploy_data))


if __name__ == "__main__":
    global rc
    rc = redis.Redis(host='redis', port=6379)
    config_to_redis()
    inventory_to_redis()
    deployment_to_redis()

