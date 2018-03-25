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
import logging
from time import sleep

import sys
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import spidev

logging.basicConfig(level=config.get_logging_level(),
                    format=config.runtime_variables['log_format'],
                    datefmt=config.runtime_variables['log_date_format'])

GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)
radio = NRF24(GPIO, spidev.SpiDev())

def configure_radio():
    #pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]
    #pipes2 = [[0xE9, 0xE9, 0xF0, 0xF0, 0xE1], [0xF1, 0xF1, 0xF0, 0xF0, 0xE1]]

    radio.begin(0, config.remote_arduino_sensor['gpio_port'])

    radio.setPayloadSize(32)
    radio.setChannel(0x76)
    #radio.setDataRate(NRF24.BR_250KBPS)
    radio.setDataRate(NRF24.BR_1MBPS)
    radio.setPALevel(NRF24.PA_MIN)

    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()

    for sensor in config.remote_arduino_sensor['sensors']:
        #logging.debug("pipe index %s, is pipe w %s" % (sensor['pipes_index'][0], sensor['pipes'][0]))
        logging.debug("pipe index %s, is pipe r %s" % (sensor['pipes_index'][1], sensor['pipes'][1]))
        #radio.openWritingPipe(sensor['pipes_index'][0], sensor['pipes'][0])
        #radio.openWritingPipe(sensor['pipes'][0])
        radio.openReadingPipe(sensor['pipes_index'][1], sensor['pipes'][1])
        #radio.openWritingPipe(1, pipes[0])
        #radio.openReadingPipe(2, pipes[1])
        #radio.openWritingPipe(3, pipes2[0])
        #radio.openReadingPipe(4, pipes2[1])

    logging.debug("Radio configured")
    #radio.printDetails()
    # radio.startListening()

def get_remote_sensor_data(sensor_config):
    message = list("GETREADINGS")
    while len(message) < 32:
        message.append(0)

    start = time.time()
    logging.debug("pipe index %s, is pipe w %s" % (sensor_config['pipes_index'][0], sensor_config['pipes'][0]))
    radio.openWritingPipe(sensor_config['pipes'][0])
    radio.write(message)
    radio.startListening()

    #is_available, pipe = radio.available_pipe()
    #while not is_available and pipe == (sensor_config['pipes_index'][1]):
    while not radio.available():
        time.sleep(1 / 100)
        if time.time() - start > 5: #Wait 5 seconds
            break
        #is_available, pipe = radio.available_pipe()

    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())

    string = ""
    for n in receivedMessage:
        # Decode into standard unicode set
        if (n >= 32 and n <= 126):
            string += chr(n)
    response = "{}".format(string)

    logging.debug("read '%s' from index %s, and pipe %s" % (response, sensor_config['pipes_index'][1], sensor_config['pipes'][1]))
    
    #T: 18.80 - H: 53.90O
    pattern = re.compile("T: (\d+.\d*) - H: (\d+.\d*)", re.IGNORECASE)
    logging.debug("Got response from remote: %s" % response) 
    result = pattern.search(response)
    if result is None:
        radio.stopListening()
        return None, None
    T = result.group(1)
    RH = result.group(2)
    radio.stopListening()
    return RH, T

def main():
    logging.info("Saving to file: %s" % (config.file['save_to_file']))
    logging.info("Saving to DB: %s" % (config.mysql['save_to_DB']))
    logging.info("Starting loop")
    try:
        configure_radio()
        while True:
            for sensor in config.remote_arduino_sensor['sensors']:
                now = datetime.datetime.utcnow()

                RRH, RT = get_remote_sensor_data(sensor)
                commonFunctions.save_humidity_data(sensor['location_name'], RRH, now.isoformat(), now.isoformat())
                commonFunctions.save_temperature_data(sensor['location_name'], RT, now.isoformat(), now.isoformat())
                logging.debug("Read Temp %s and Humidity %s from Remote %s" % (RT, RRH, sensor['location_name']))
            
            sleep(config.remote_arduino_sensor['sleep_time_in_seconds_between_reads'])
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
