#!/usr/bin/env python

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

local_sensor = { 'gpio_port': 23,
                 'location_name': "Dining",
                 'sleep_time_in_seconds_between_reads': 60.0,
                  }

remote_arduino_sensor = { 'gpio_port': 17,
                          'location_name': "Room",
                          'sleep_time_in_seconds_between_reads': 60.0,
                           }

runtime_variables = { 'debug' : True,
                      'log_format' : '%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',
                      'log_date_format' : '%H:%M:%S',
                      'sleep_time_in_seconds_between_reads' : 60.0,
                       }                    

webapp = { 'listening_ip': '0.0.0.0',
            }

def get_logging_level():
  if runtime_variables['debug']:
    return logging.DEBUG
  return logging.INFO