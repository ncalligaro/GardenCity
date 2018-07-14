#!/usr/bin/env python
from config import config

import commonFunctions
import logging
import threading

import ConfigParser
import json
from tinydb import TinyDB, Query, where

logging.basicConfig(level=config.get_logging_level(),
                    format=config.runtime_variables['log_format'],
                    datefmt=config.runtime_variables['log_date_format'])

runtime_config = ConfigParser.ConfigParser()

RUNTIME_CONFIG_FILE_PATH = 'config/runtimeSettings.json'
runtime_config_lock = threading.BoundedSemaphore(value=1)

SCHEDULE_CONFIG_FILE_PATH = 'config/schedulesDB.json'

CLIENT_SECRETS_FILE = "config/client_secret.json"

def get_runtime_config():
  runtime_config_lock.acquire()
  with open(RUNTIME_CONFIG_FILE_PATH, 'r') as f:
    runtime_config = json.load(f)
    runtime_config_lock.release()
    return runtime_config

def save_runtime_config(newConfig):
  runtime_config_lock.acquire()
  with open(RUNTIME_CONFIG_FILE_PATH, 'w') as f:
    json.dump(newConfig, f)
  runtime_config_lock.release()
  return get_runtime_config()

def get_schedule_table():
  db = TinyDB(SCHEDULE_CONFIG_FILE_PATH)
  return db.table('schedules')  

def get_client_secret():
  with open(CLIENT_SECRETS_FILE, 'r') as f:
    client_secret = json.load(f)
    return client_secret['web']['client_secret']
