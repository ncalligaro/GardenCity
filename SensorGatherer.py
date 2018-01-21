#!/usr/bin/python
from __future__ import print_function
import sys
import serial
import datetime
import time
import re
import traceback
import config
import httplib
import urllib
import json

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
MEASUREMENT_TYPE_PRESSURE = 'pressure'
MEASUREMENT_TYPE_WIND = 'wind'
MEASUREMENT_TYPE_TEMPERATURE_RANGE_MIN = 'temperature_min'
MEASUREMENT_TYPE_TEMPERATURE_RANGE_MAX = 'temperature_max'
MEASUREMENT_TYPE_VISIBILITY = 'visibility'
MEASUREMENT_TYPE_RAIN = 'rain'
MEASUREMENT_TYPE_CLOUDS = 'clouds'
MEASUREMENT_TYPE_SUNRISE = 'sunrise'
MEASUREMENT_TYPE_SUNSET = 'sunset'


SAVE_TO_FILE = config.file['save_to_file']
SAVE_TO_DB = config.mysql['save_to_DB']

def get_from_dic(dictionary, field1, field2 = None):
    if dictionary is None:
        return None
    if dictionary.get(field1) is None:
        return None
    if field2 is None:
        return dictionary.get(field1)
    if dictionary.get(field1).get(field2) is None:
        return None
    return dictionary.get(field1).get(field2)

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

def get_dining_sensor_data():
    RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, LOCAL_TEMPERATURE_HUMIDITY_SENSOR_PORT)
    if RH is not None and T is not None:
        return (str(RH), str(T))
    else:
        return None, None

def get_current_city_data():
    http_connection = httplib.HTTPSConnection(config.open_map['host'])
    http_connection.request("GET", ("%s?q=%s&units=%s&appid=%s" % (config.open_map['path'], config.open_map['city'], 'metric', config.open_map['api_key'])))
    response = http_connection.getresponse()
    #if (response.status != httplib.OK):
    #    print 'Error ocurred'
    #    print response.status, response.reason
    #    return None #Replace this with an exception
    #else:
    jsondata = response.read()
    data = json.loads(jsondata)
    return data

def get_room_sensor_data():
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

def save_openweather_map_info_to_DB(json_data, creation_time):
    current_place = get_from_dic(json_data, 'name')
    place = "city_%s" % current_place
    measurement_date = get_from_dic(json_data, 'dt')

    current_temperature = get_from_dic(json_data, 'main', 'temp')
    current_pressure = get_from_dic(json_data, 'main', 'pressure')
    current_humidity = get_from_dic(json_data, 'main', 'humidity')
    current_temperature_min = get_from_dic(json_data, 'main', 'temp_min')
    current_temperature_max = get_from_dic(json_data, 'main', 'temp_max')
    current_rain = get_from_dic(json_data, 'rain', '3h')
    current_visibility = get_from_dic(json_data, 'visibility')
    current_wind_speed = get_from_dic(json_data, 'wind', 'speed')
    current_wind_direction = get_from_dic(json_data, 'wind', 'deg')
    current_clouds = get_from_dic(json_data, 'clouds', 'all')
    current_sunrise = get_from_dic(json_data, 'sys', 'sunrise')
    current_sunset = get_from_dic(json_data, 'sys', 'sunset')  

    save_temperature_data(place, current_temperature, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    save_pressure_data(place, current_pressure, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    save_humidity_data(place, current_humidity, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    save_temperature_range_min_data(place, current_temperature_min, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    save_temperature_range_max_data(place, current_temperature_max, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    save_rain_data(place, current_rain, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    save_visibility_data(place, current_visibility, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    save_wind_data(place, current_wind_speed, current_wind_direction, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    save_clouds_data(place, current_clouds, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    save_sunrise_data(place, current_sunrise, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    save_sunset_data(place, current_sunset, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)


def save_two_value_record(place, value, second_value, value_type, unit, measurement_date, creation_time):
    if value is None or value_type is None:
        value = 'null'
    if second_value is None:
        second_value = 'null'

    if 'FROM_UNIXTIME' not in measurement_date:
        measurement_date = "'%s'" % measurement_date

    sql_sentence = ("INSERT INTO measurement (place,type,value,value2,unit,measurement_date,created_at) VALUES ('%s','%s',%s,'%s','%s',%s,'%s');\n" % (place, value_type, value, second_value, unit, measurement_date, creation_time))

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
            #First check if record already exists

            #Commenting this whole thing because sometimes the web feed sometimes returns different values for the same measurement date
            #second_value_query = second_value
            #if second_value_query != 'null':
            #    second_value_query = "value2 = '%s'" % second_value
            #else:
            #    second_value_query = "1=1"
            #query_sentence = ("SELECT * FROM measurement where place = '%s' AND type = '%s' AND measurement_date = %s and value = %s AND %s" % (place, value_type, measurement_date, value, second_value_query))
            query_sentence = ("SELECT * FROM measurement where place = '%s' AND type = '%s' AND measurement_date = %s" % (place, value_type, measurement_date))
            error_print("query_sentence: %s" % query_sentence)
            cursor.execute(query_sentence)
            cursor.fetchall()
            error_print(cursor.rowcount)
            if int(cursor.rowcount) == 0:
                cursor.close()
                cursor = db_connection.cursor()
                cursor.execute(sql_sentence)
                db_connection.commit()
            else:
                error_print("Values already exist in DB: %s" % sql_sentence)
        except mariadb.Error as error:
            error_print("Error saving to DB: {}".format(error))
        finally:
            if db_connection is not None:
                db_connection.close()

def save_record(place, value, value_type, unit, measurement_date, creation_time):
    save_two_value_record(place, value, None, value_type, unit, measurement_date, creation_time)

def save_humidity_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_record(place, value, MEASUREMENT_TYPE_HUMIDITY, 'P', measurement_date, creation_time)

def save_temperature_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_record(place, value, MEASUREMENT_TYPE_TEMPERATURE, 'C', measurement_date, creation_time)

def save_pressure_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_record(place, value, MEASUREMENT_TYPE_PRESSURE, 'hPa', measurement_date, creation_time)

def save_wind_data(place, value, direction, measurement_date, creation_time):
    if value is not None:
        save_two_value_record(place, value, direction, MEASUREMENT_TYPE_WIND, 'MtsPS', measurement_date, creation_time)

def save_temperature_range_min_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_record(place, value, MEASUREMENT_TYPE_TEMPERATURE_RANGE_MIN, 'C', measurement_date, creation_time)

def save_temperature_range_max_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_record(place, value, MEASUREMENT_TYPE_TEMPERATURE_RANGE_MAX, 'C', measurement_date, creation_time)

def save_visibility_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_record(place, value, MEASUREMENT_TYPE_VISIBILITY, 'Mts', measurement_date, creation_time)

def save_rain_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_record(place, value, MEASUREMENT_TYPE_RAIN, 'CM3', measurement_date, creation_time)

def save_clouds_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_record(place, value, MEASUREMENT_TYPE_CLOUDS, 'P', measurement_date, creation_time)

def save_sunrise_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_record(place, value, MEASUREMENT_TYPE_SUNRISE, 'Hs', measurement_date, creation_time)
def save_sunset_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_record(place, value, MEASUREMENT_TYPE_SUNSET, 'Hs', measurement_date, creation_time)

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

            DRH, DT = get_dining_sensor_data()
            save_humidity_data(LOCATION_DINING, DRH, now.isoformat(), now.isoformat())
            save_temperature_data(LOCATION_DINING, DT, now.isoformat(), now.isoformat())
            
            RRH, RT = get_room_sensor_data()
            save_humidity_data(LOCATION_ROOM, RRH, now.isoformat(), now.isoformat())
            save_temperature_data(LOCATION_ROOM, RT, now.isoformat(), now.isoformat())
            
            openweathermap_jsondata = get_current_city_data()
            save_openweather_map_info_to_DB(openweathermap_jsondata, now.isoformat())

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
