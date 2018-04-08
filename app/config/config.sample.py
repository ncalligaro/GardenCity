#!/usr/bin/env python
import logging

mysql = { 'host': '',
          'user': '',
          'password':'',
          'database':'',
          'save_to_DB': True,
           }

file = { 'save_to_file': True,
    		 #'suffix' : '%Y-%m-%d_%H%M',
    		 'suffix' : '%Y-%m-%d',
    		 'path' : 'someFolderWithinCurrentPWD',
          }

open_map = { 'host': 'api.openweathermap.org',
             'path': '/data/2.5/weather',
             'api_key': '',
			       'city': 'London,uk',
             'sleep_time_in_seconds_between_reads': 60.0*30,
              }

local_sensors = { 'sleep_time_in_seconds_between_reads': 60.0,
                  'sensors': [
                    { 'gpio_port': 23,
                      'location_name': 'Kitchen',
                      'sensor_model': 'DHT22',
                    }]
                }

presence_sensor = { 'sleep_time_in_seconds_between_reads': 60.0,
                     }

remote_arduino_sensors = [{ 'gpio_port': 17,
                          'location_name': "Room",
                          'sleep_time_in_seconds_between_reads': 60.0,
                          'pipes': [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]
                           }]

runtime_variables = { 'debug' : True,
                      'log_format' : '%(asctime)s [%(levelname)s] (%(threadName)-10s) %(filename)s:%(lineno)d %(message)s',
                      'log_date_format' : '%H:%M:%S',
                       }      

boiler = { 'temperature_margin' : 0.5,
           'sleep_time_in_seconds_between_checks' : 60.0,
           }

webapp = { 'listening_ip': '0.0.0.0',
           'sslConfig': ('config/fullchain.pem', 'config/privkey.pem'),
            }

def get_logging_level():
  if runtime_variables['debug']:
    return logging.DEBUG
  return logging.INFO