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
                      'location_name': 'Location Name 1',
                      'sensor_model': 'DHT22',
                      'variation_margin_units': 10,
                    },
                    { 'gpio_port': 22,
                      'location_name': 'Location Name 2',
                      'sensor_model': 'DS18B20',
                      'id': '<SENSOR_ID>',
                      'variation_margin_units': 50,
                    }]
                }

remote_arduino_sensor = { 'sleep_time_in_seconds_between_reads': 60.0,
                          'gpio_port': 17,
                          'sensors': [
                            { 'location_name': "Location Name 3",
                              'pipes': [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]],
                              'pipes_index': [0,1],
                            }
                           ]
                        }

runtime_variables = { 'debug' : True,
                      'log_format' : '%(asctime)s [%(levelname)s] (%(threadName)-10s) %(filename)s:%(lineno)d %(message)s',
                      'log_date_format' : '%H:%M:%S',
                       }      

boiler = { 'sleep_time_in_seconds_between_checks' : 60.0,
           'gpio_port': 3,
           }

webapp = { 'listening_ip': '0.0.0.0',
           'sslConfig': ('config/fullchain.pem', 'config/privkey.pem'),
            }

def get_logging_level():
  if runtime_variables['debug']:
    return logging.DEBUG
  return logging.INFO