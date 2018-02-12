#!/usr/bin/python
from config import config

import commonFunctions

#from __future__ import print_function
import sys
import serial
import datetime
import time
from time import sleep
import re
import traceback
import json
import logging

import sys
import RPi.GPIO as GPIO
#import spidev

import Adafruit_DHT

logging.basicConfig(level=config.get_logging_level(),
                    format=config.runtime_variables['log_format'],
                    datefmt=config.runtime_variables['log_date_format'])

GPIO.setmode(GPIO.BCM)

def get_local_sensor_data():
    RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, config.local_sensor['gpio_port'])
    if RH is not None and T is not None:
        return (str(RH), str(T))
    else:
        return None, None

def main():
    logging.info("Saving to file: %s" % (config.file['save_to_file']))
    logging.info("Saving to DB: %s" % (config.mysql['save_to_DB']))
    logging.info("Starting loop")
    try:
        while True:
            now = datetime.datetime.utcnow()

            LRH, LT = get_local_sensor_data()
            commonFunctions.save_humidity_data(config.local_sensor['location_name'], LRH, now.isoformat(), now.isoformat())
            commonFunctions.save_temperature_data(config.local_sensor['location_name'], LT, now.isoformat(), now.isoformat())

            sleep(config.local_sensor['sleep_time_in_seconds_between_reads'])
    except KeyboardInterrupt:
        logging.error("\nbye!")
        sys.exit(1)
    except Exception as e:
        logging.error("\nOther error occurred")
        logging.error (e)
        logging.error(traceback.format_exc())
        sys.exit(1)
    finally:
        logging.info("\nCleaning GPIO port\n")
        GPIO.cleanup()

# call main
if __name__ == '__main__':
   main()
