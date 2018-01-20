#!/usr/bin/python
import serial
import datetime
import time
import re
import traceback

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
MEASUREMENTS_FOLDER = 'measurements'

SAVE_TO_FILE = True
SAVE_TO_DB = True

def connect_to_db():
    try:
        return mariadb.connect(user='XX', password='XX', host='XX', database='XX')
    except mariadb.Error as error:
        print("Error opening connection to DB: {}".format(error))
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

def save_record(place, value, valueType, measureTime, creationTime):

    sqlSentence = None
    if value is not None and valueType is not None:
        sqlSentence = ("INSERT INTO measurement (place,type,value,unit,measurement_date,created_at) VALUES ('%s','%s',%s,'P','%s','%s');\n" % (place, valueType, value, measureTime, creationTime))
    else:
        sqlSentence = ("INSERT INTO measurement (place,type,value,unit,measurement_date,created_at) VALUES ('%s','%s',%s,'P','%s','%s');\n" % (place, valueType, 'null', measureTime, creationTime))
    
    if (SAVE_TO_FILE):
        try:
            f = open('%s/temps_%s.txt' % (MEASUREMENTS_FOLDER, SCRIPT_START_DATE.strftime("%Y-%m-%d_%H%M")),'a')
            #SAVE
            f.write(sqlSentence)
            f.close()
        except Error as error:
            print("Error saving to file: {}".format(error))

    if (SAVE_TO_DB):
        db_connection = None
        try:
            db_connection = connect_to_db()
            cursor = db_connection.cursor()
            cursor.execute(sqlSentence)
            db_connection.commit()
        except mariadb.Error as error:
            print("Error saving to DB: {}".format(error))
        finally:
            if db_connection is not None:
                db_connection.close()


def main():
    try:
        configure_radio()
        while True:
            now = datetime.datetime.utcnow()

            DRH, DT = get_local_sensor_data()
            save_record('Dining', DRH, 'humidity', now.isoformat(), now.isoformat())
            save_record('Dining', DT, 'temperature', now.isoformat(), now.isoformat())

            RRH, RT = get_remote_sensor_data()
            save_record('Room', RRH, 'humidity', now.isoformat(), now.isoformat())
            save_record('Room', RT, 'temperature', now.isoformat(), now.isoformat())

            time.sleep(60)
    except KeyboardInterrupt:
        print "\nbye!"
    except Exception as e:
        print "\nOther error occurred"
        print (e)
        print(traceback.format_exc())
    finally:
        print "\nCleaning GPIO port\n"
        GPIO.cleanup()

# call main
if __name__ == '__main__':
   main()
