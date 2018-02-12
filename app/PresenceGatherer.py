#!/usr/bin/python
from config import config

import commonFunctions

#from __future__ import print_function
# import sys
# import serial
import datetime
import time
import logging
# import re
import traceback
# import json
from time import sleep
# import sys

import pyping
# Note, does not work because both android and iphone stop responding to pings after a little while of being on standby

logging.basicConfig(level=config.get_logging_level(),
                    format=config.runtime_variables['log_format'],
                    datefmt=config.runtime_variables['log_date_format'])

def get_local_presence_data(location_name, presence_name):
    ip = ''
    if presence_name == 'Nico':
        ip = "192.168.0.77"
    if presence_name == 'Flor':
        ip = "192.168.0.31"
    response = pyping.ping(ip)
    logging.debug (presence_name + ' ' + str(response.ret_code))
    return (response.ret_code == 0); #0 = reachable, other is unreachable

def main():
    logging.info("Saving to file: %s" % (config.file['save_to_file']))
    logging.info("Saving to DB: %s" % (config.mysql['save_to_DB']))
    logging.info("Starting loop")
    try:
        while True:
            now = datetime.datetime.utcnow()

            nico = get_local_presence_data('Home','Nico')
            flor = get_local_presence_data('Home','Flor')

            commonFunctions.save_presence_data('Home', 'Nico', nico, now.isoformat(), now.isoformat())
            commonFunctions.save_presence_data('Home', 'Flor', flor, now.isoformat(), now.isoformat())

            sleep(config.presence_sensor['sleep_time_in_seconds_between_reads'])
    except KeyboardInterrupt:
        logging.error("\nbye!")
    except Exception as e:
        logging.error("\nOther error occurred")
        logging.error (e)
        logging.error(traceback.format_exc())
    finally:
        logging.info("\nBye 2!\n")

# call main
if __name__ == '__main__':
   main()
