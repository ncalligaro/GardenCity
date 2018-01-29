#!/usr/bin/python
from config import config

import commonFunctions

#from __future__ import print_function
# import sys
# import serial
import datetime
import time
# import re
import traceback
# import json

# import sys

import pyping
# Note, does not work because both android and iphone stop responding to pings after a little while of being on standby

def get_local_presence_data(location_name, presence_name):
    ip = ''
    if presence_name == 'Nico':
        ip = "192.168.0.77"
    if presence_name == 'Flor':
        ip = "192.168.0.31"
    response = pyping.ping(ip)
    print (presence_name + ' ' + str(response.ret_code))
    return (response.ret_code == 0); #0 = reachable, other is unreachable

def main():
    commonFunctions.error_print("Saving to file: %s" % (config.file['save_to_file']))
    commonFunctions.error_print("Saving to DB: %s" % (config.mysql['save_to_DB']))
    commonFunctions.error_print("Starting loop")
    try:
        while True:
            now = datetime.datetime.utcnow()

            nico = get_local_presence_data('Home','Nico')
            flor = get_local_presence_data('Home','Flor')

            commonFunctions.save_presence_data('Home', 'Nico', nico, now.isoformat(), now.isoformat())
            commonFunctions.save_presence_data('Home', 'Flor', flor, now.isoformat(), now.isoformat())

            time.sleep(5)
    except KeyboardInterrupt:
        print("\nbye!")
    except Exception as e:
        print("\nOther error occurred")
        print (e)
        print(traceback.format_exc())
    finally:
        print("\nBye 2!\n")

# call main
if __name__ == '__main__':
   main()
