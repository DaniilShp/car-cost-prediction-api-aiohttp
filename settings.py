import os
import json


def get_config():
    return {'app_host': '127.0.0.1', 'app_port': 8081}


def get_db_config():
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    dbconfig_path = os.path.join(current_dir, 'configs', 'dbconfig.json')
    with open(dbconfig_path, 'r') as f:
        dbconfig = json.load(f)
    return dbconfig

