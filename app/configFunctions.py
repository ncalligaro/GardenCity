#!/usr/bin/env python
from config import config

import commonFunctions
import logging

import ConfigParser
import json
from tinydb import TinyDB, Query, where

logging.basicConfig(level=config.get_logging_level(),
                    format=config.runtime_variables['log_format'],
                    datefmt=config.runtime_variables['log_date_format'])



runtime_config = ConfigParser.ConfigParser()
runtime_config_file_path = 'config/runtimeSettings.json'
schedule_config_file_path = 'config/schedulesDB.json'

def get_runtime_config():
  with open(runtime_config_file_path, 'r') as f:
    runtime_config = json.load(f)
    return runtime_config

def save_runtime_config(newConfig):
  with open(runtime_config_file_path, 'w') as f:
    json.dump(newConfig, f)
  return get_runtime_config()

def getScheduleTable():
  db = TinyDB(schedule_config_file_path)
  return db.table('schedules')  

