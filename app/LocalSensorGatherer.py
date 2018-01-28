#!/usr/bin/python
from config import config

import commonFunctions

#from __future__ import print_function
import sys
import serial
import datetime
import time
import re
import traceback
import json

import sys
import RPi.GPIO as GPIO
#import spidev

import Adafruit_DHT

GPIO.setmode(GPIO.BCM)

def get_local_sensor_data():
    RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, config.local_sensor['gpio_port'])
    if RH is not None and T is not None:
        return (str(RH), str(T))
    else:
        return None, None

def main():
    commonFunctions.error_print("Saving to file: %s" % (config.file['save_to_file']))
    commonFunctions.error_print("Saving to DB: %s" % (config.mysql['save_to_DB']))
    commonFunctions.error_print("Starting loop")
    try:
        while True:
            now = datetime.datetime.utcnow()

            LRH, LT = get_local_sensor_data()
            commonFunctions.save_humidity_data(config.local_sensor['location_name'], LRH, now.isoformat(), now.isoformat())
            commonFunctions.save_temperature_data(config.local_sensor['location_name'], LT, now.isoformat(), now.isoformat())

            time.sleep(60)
    except KeyboardInterrupt:
        print("\nbye!")
    except Exception as e:
        print("\nOther error occurred")
        print (e)
        print(traceback.format_exc())
    finally:
        print("\nCleaning GPIO port\n")
        GPIO.cleanup()

# call main
if __name__ == '__main__':
   main()
