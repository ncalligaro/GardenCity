#!/usr/bin/python
from __future__ import print_function
from config import config

import sys
#import serial
import datetime
import time
import re
#import traceback
#import httplib
#import urllib
#import json

import mysql.connector as mariadb

import sys
#import RPi.GPIO as GPIO
#from lib_nrf24 import NRF24
#import spidev

#import Adafruit_DHT

SCRIPT_START_DATE = datetime.datetime.utcnow()
MEASUREMENTS_FOLDER = config.file['path']
MEASUREMENTS_FILE_SUFFIX = config.file['suffix']

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

def fix_measurement_date(measurement_date):
    if 'FROM_UNIXTIME' not in measurement_date:
        return "'%s'" % measurement_date
    return measurement_date


def save_two_value_record(place, value, second_value, value_type, unit, measurement_date, creation_time):
    if value is None or value_type is None:
        value = 'null'
    if second_value is None:
        second_value = 'null'

    measurement_date = fix_measurement_date(measurement_date)

    sql_sentence = ("INSERT INTO measurement (place,type,value,value2,unit,measurement_date,created_at) VALUES ('%s','%s',%s,'%s','%s',%s,'%s');\n" % (place, value_type, value, second_value, unit, measurement_date, creation_time))

    if (config.file['save_to_file']):
        try:
            f = open('%s/temps_%s.log' % (MEASUREMENTS_FOLDER, SCRIPT_START_DATE.strftime(MEASUREMENTS_FILE_SUFFIX)),'a')
            f.write(sql_sentence)
            f.close()
        except IOError as error:
            error_print("Error saving to file: {}".format(error))

    if (config.mysql['save_to_DB']):
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
            #error_print("query_sentence: %s" % query_sentence)
            cursor.execute(query_sentence)
            cursor.fetchall()
            #error_print(cursor.rowcount)
            if int(cursor.rowcount) == 0:
                cursor.close()
                cursor = db_connection.cursor()
                cursor.execute(sql_sentence)
                db_connection.commit()
            #else:
                #error_print("Values already exist in DB: %s" % sql_sentence)
        except mariadb.Error as error:
            error_print("Error saving to DB: {}".format(error))
        finally:
            if db_connection is not None:
                db_connection.close()

def save_heater_record(state, reason, reason_explanation, measurement_date, creation_time):
    measurement_date = fix_measurement_date(measurement_date)

    sql_sentence = ("INSERT INTO heater (state,reason,reason_explanation,measurement_date,created_at) VALUES ('%s','%s','%s',%s,'%s');\n" % (state, reason, reason_explanation, measurement_date, creation_time))

    if (config.file['save_to_file']):
        try:
            f = open('%s/heater_%s.log' % (MEASUREMENTS_FOLDER, SCRIPT_START_DATE.strftime(MEASUREMENTS_FILE_SUFFIX)),'a')
            f.write(sql_sentence)
            f.close()
        except IOError as error:
            error_print("Error saving to file: {}".format(error))

    if (config.mysql['save_to_DB']):
        db_connection = None
        try:
            db_connection = connect_to_db()
            cursor = db_connection.cursor()

            # query_sentence = ("SELECT * FROM heater where place = '%s' AND person = '%s' AND measurement_date = %s" % (place, person, measurement_date))
            # cursor.execute(query_sentence)
            # cursor.fetchall()
            # if int(cursor.rowcount) == 0:
                # cursor.close()
            cursor = db_connection.cursor()
            cursor.execute(sql_sentence)
            db_connection.commit()
        except mariadb.Error as error:
            error_print("Error saving to DB: {}".format(error))
        finally:
            if db_connection is not None:
                db_connection.close()

def save_presence_record(place, person, presence, measurement_date, creation_time):
    measurement_date = fix_measurement_date(measurement_date)

    sql_sentence = ("INSERT INTO presence (place,person,presence,measurement_date,created_at) VALUES ('%s','%s',%s,%s,'%s');\n" % (place, person, presence, measurement_date, creation_time))

    if (config.file['save_to_file']):
        try:
            f = open('%s/presence_%s.log' % (MEASUREMENTS_FOLDER, SCRIPT_START_DATE.strftime(MEASUREMENTS_FILE_SUFFIX)),'a')
            f.write(sql_sentence)
            f.close()
        except IOError as error:
            error_print("Error saving to file: {}".format(error))

    if (config.mysql['save_to_DB']):
        db_connection = None
        try:

            db_connection = connect_to_db()
            cursor = db_connection.cursor()

            query_sentence = ("SELECT * FROM presence where place = '%s' AND person = '%s' AND measurement_date = %s" % (place, person, measurement_date))
            cursor.execute(query_sentence)
            cursor.fetchall()
            if int(cursor.rowcount) == 0:
                cursor.close()
                cursor = db_connection.cursor()
                cursor.execute(sql_sentence)
                db_connection.commit()
        except mariadb.Error as error:
            error_print("Error saving to DB: {}".format(error))
        finally:
            if db_connection is not None:
                db_connection.close()

def save_measurement_record(place, value, value_type, unit, measurement_date, creation_time):
    save_two_value_record(place, value, None, value_type, unit, measurement_date, creation_time)

def save_humidity_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_measurement_record(place, value, MEASUREMENT_TYPE_HUMIDITY, 'P', measurement_date, creation_time)

def save_temperature_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_measurement_record(place, value, MEASUREMENT_TYPE_TEMPERATURE, 'C', measurement_date, creation_time)

def save_pressure_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_measurement_record(place, value, MEASUREMENT_TYPE_PRESSURE, 'hPa', measurement_date, creation_time)

def save_wind_data(place, value, direction, measurement_date, creation_time):
    if value is not None:
        save_two_value_record(place, value, direction, MEASUREMENT_TYPE_WIND, 'MtsPS', measurement_date, creation_time)

def save_temperature_range_min_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_measurement_record(place, value, MEASUREMENT_TYPE_TEMPERATURE_RANGE_MIN, 'C', measurement_date, creation_time)

def save_temperature_range_max_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_measurement_record(place, value, MEASUREMENT_TYPE_TEMPERATURE_RANGE_MAX, 'C', measurement_date, creation_time)

def save_visibility_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_measurement_record(place, value, MEASUREMENT_TYPE_VISIBILITY, 'Mts', measurement_date, creation_time)

def save_rain_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_measurement_record(place, value, MEASUREMENT_TYPE_RAIN, 'CM3', measurement_date, creation_time)

def save_clouds_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_measurement_record(place, value, MEASUREMENT_TYPE_CLOUDS, 'P', measurement_date, creation_time)

def save_sunrise_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_measurement_record(place, value, MEASUREMENT_TYPE_SUNRISE, 'Hs', measurement_date, creation_time)

def save_sunset_data(place, value, measurement_date, creation_time):
    if value is not None:
        save_measurement_record(place, value, MEASUREMENT_TYPE_SUNSET, 'Hs', measurement_date, creation_time)

def save_presence_data(place, person, presence, measurement_date, creation_time):
    if person is not None and presence is not None:
        save_presence_record(place, person, presence, measurement_date, creation_time)

def save_heater_data(state, reason, reason_explanation, measurement_date, creation_time):
    if state is not None and reason is not None and measurement_date is not None:
        save_heater_record(state, reason, reason_explanation, measurement_date, creation_time)

def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

