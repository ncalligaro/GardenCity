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
import httplib
import urllib
import json

import sys
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import spidev

GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)
radio = NRF24(GPIO, spidev.SpiDev())

def configure_radio():
    pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]

    radio.begin(0, config.remote_arduino_sensor['gpio_port'])

    radio.setPayloadSize(32)
    radio.setChannel(0x76)
    radio.setDataRate(NRF24.BR_1MBPS)
    radio.setPALevel(NRF24.PA_MIN)

    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()

    radio.openWritingPipe(pipes[0])
    radio.openReadingPipe(1, pipes[1])
    #radio.printDetails()
    # radio.startListening()

def get_remote_sensor_data():
    message = list("GETREADINGS")
    while len(message) < 32:
        message.append(0)

    start = time.time()
    radio.write(message)
    radio.startListening()

    while not radio.available(0):
        time.sleep(1 / 100)
        if time.time() - start > 5: #Wait 5 seconds
            break

    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())

    string = ""
    for n in receivedMessage:
        # Decode into standard unicode set
        if (n >= 32 and n <= 126):
            string += chr(n)
    response = "{}".format(string)
    #T: 18.80 - H: 53.90O
    pattern = re.compile("T: (\d+.\d*) - H: (\d+.\d*)", re.IGNORECASE)
    result = pattern.search(response)
    if result is None:
        radio.stopListening()
        return None, None
    T = result.group(1)
    RH = result.group(2)
    radio.stopListening()
    return RH, T

def main():
    commonFunctions.error_print("Saving to file: %s" % (config.file['save_to_file']))
    commonFunctions.error_print("Saving to DB: %s" % (config.mysql['save_to_DB']))
    commonFunctions.error_print("Starting loop")
    try:
        configure_radio()
        while True:
            now = datetime.datetime.utcnow()

            RRH, RT = get_remote_sensor_data()
            commonFunctions.save_humidity_data(config.remote_arduino_sensor['location_name'], RRH, now.isoformat(), now.isoformat())
            commonFunctions.save_temperature_data(config.remote_arduino_sensor['location_name'], RT, now.isoformat(), now.isoformat())
            
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
