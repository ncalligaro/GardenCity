#!/usr/bin/python
import config

import commonFunctions

from __future__ import print_function
import sys
import datetime
import time
import re
import traceback
import httplib
import urllib
import json
import sys

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

def main():
    error_print("Saving to file: %s" % (SAVE_TO_FILE))
    error_print("Saving to DB: %s" % (SAVE_TO_DB))
    error_print("Starting loop")
    try:
        while True:
            now = datetime.datetime.utcnow()
    
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
        print("\nbye2!")
        #print("\nCleaning GPIO port\n")
        #GPIO.cleanup()

# call main
if __name__ == '__main__':
   main()
