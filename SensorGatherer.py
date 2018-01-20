#!/usr/bin/python
from __future__ import print_function
import sys
import serial
import datetime
import time
import re
import traceback
import config

import mysql.connector as mariadb

import sys
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import spidev

import Adafruit_DHT
#import urllib2

LOCAL_TEMPERATURE_HUMIDITY_SENSOR_PORT = 23;  #BCM format

GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)
radio = NRF24(GPIO, spidev.SpiDev())

SCRIPT_START_DATE = datetime.datetime.utcnow()
MEASUREMENTS_FOLDER = config.file['path']
MEASUREMENTS_FILE_SUFFIX = config.file['suffix']

LOCATION_DINING = 'Dining'
LOCATION_ROOM = 'Room'

MEASUREMENT_TYPE_HUMIDITY = 'humidity'
MEASUREMENT_TYPE_TEMPERATURE = 'temperature'

SAVE_TO_FILE = config.file['save_to_file']
SAVE_TO_DB = config.mysql['save_to_DB']

def connect_to_db():
    try:
        return mariadb.connect(user=config.mysql['user'], password=config.mysql['password'], host=config.mysql['host'], database=config.mysql['database'])
    except mariadb.Error as error:
        error_print("Error opening connection to DB: {}".format(error))
        raise

def configure_radio():
    pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]

    radio.begin(0, 17)

    radio.setPayloadSize(32)
    radio.setChannel(0x76)
    radio.setDataRate(NRF24.BR_1MBPS)
    radio.setPALevel(NRF24.PA_MIN)

    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()

    radio.openWritingPipe(pipes[0])
    radio.openReadingPipe(1, pipes[1])
    radio.printDetails()
    # radio.startListening()

def get_local_sensor_data():
    RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, LOCAL_TEMPERATURE_HUMIDITY_SENSOR_PORT)
    if RH is not None and T is not None:
        return (str(RH), str(T))
    else:
        return None, None

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

def save_record(place, value, value_type, unit, measure_time, creation_time):

    if value is None or value_type is None:
        value = 'null'

    sql_sentence = ("INSERT INTO measurement (place,type,value,unit,measurement_date,created_at) VALUES ('%s','%s',%s,'%s','%s','%s');\n" % (place, value_type, value, unit, measure_time, creation_time))

    if (SAVE_TO_FILE):
        try:
            f = open('%s/temps_%s.log' % (MEASUREMENTS_FOLDER, SCRIPT_START_DATE.strftime(MEASUREMENTS_FILE_SUFFIX)),'a')
            f.write(sql_sentence)
            f.close()
        except Error as error:
            error_print("Error saving to file: {}".format(error))

    if (SAVE_TO_DB):
        db_connection = None
        try:
            db_connection = connect_to_db()
            cursor = db_connection.cursor()
            cursor.execute(sql_sentence)
            db_connection.commit()
        except mariadb.Error as error:
            error_print("Error saving to DB: {}".format(error))
        finally:
            if db_connection is not None:
                db_connection.close()

def save_humidity_data(place, value, measurement_date)
    save_record(place, value, MEASUREMENT_TYPE_HUMIDITY, 'P', measurement_date, measurement_date)

def save_temperature_data(place, value, measurement_date)
    save_record(place, value, MEASUREMENT_TYPE_TEMPERATURE, 'C', measurement_date, measurement_date)

def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main():
    error_print("Saving to file: %s" % (SAVE_TO_FILE))
    error_print("Saving to DB: %s" % (SAVE_TO_DB))
    error_print("Starting loop")
    try:
        configure_radio()
        while True:
            now = datetime.datetime.utcnow()

            DRH, DT = get_local_sensor_data()
            save_humidity_data(LOCATION_DINING, DRH, now.isoformat())
            save_temperature_data(LOCATION_DINING, DT, now.isoformat())
            #save_record(LOCATION_DINING, DRH, MEASUREMENT_TYPE_HUMIDITY, 'P', now.isoformat(), now.isoformat())
            #save_record(LOCATION_DINING, DT, MEASUREMENT_TYPE_TEMPERATURE, 'C', now.isoformat(), now.isoformat())

            RRH, RT = get_remote_sensor_data()
            save_humidity_data(LOCATION_ROOM, RRH, now.isoformat())
            save_temperature_data(LOCATION_ROOM, RT, now.isoformat())
            #save_record(LOCATION_ROOM, RRH, MEASUREMENT_TYPE_HUMIDITY, 'P', now.isoformat(), now.isoformat())
            #save_record(LOCATION_ROOM, RT, MEASUREMENT_TYPE_TEMPERATURE, 'C', now.isoformat(), now.isoformat())

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
