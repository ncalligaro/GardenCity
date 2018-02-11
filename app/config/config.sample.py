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
              }

local_sensor = { 'gpio_port': 23,
                 'location_name': "Dining",
                  }

remote_arduino_sensor = { 'gpio_port': 17,
                          'location_name': "Room",
                           }

runtime_variables = { 'debug' : False,
                      }                    

