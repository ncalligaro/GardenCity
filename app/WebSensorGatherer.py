#!/usr/bin/python
from config import config

import commonFunctions

import datetime
import traceback
import httplib
import json
import sys
import logging
from time import sleep

logging.basicConfig(level=config.get_logging_level(),
                    format=config.runtime_variables['log_format'],
                    datefmt=config.runtime_variables['log_date_format'])

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
    current_place = commonFunctions.get_from_dic(json_data, 'name')
    place = "city_%s" % current_place
    measurement_date = commonFunctions.get_from_dic(json_data, 'dt')

    current_temperature = commonFunctions.get_from_dic(json_data, 'main', 'temp')
    current_pressure = commonFunctions.get_from_dic(json_data, 'main', 'pressure')
    current_humidity = commonFunctions.get_from_dic(json_data, 'main', 'humidity')
    current_temperature_min = commonFunctions.get_from_dic(json_data, 'main', 'temp_min')
    current_temperature_max = commonFunctions.get_from_dic(json_data, 'main', 'temp_max')
    current_rain = commonFunctions.get_from_dic(json_data, 'rain', '3h')
    current_visibility = commonFunctions.get_from_dic(json_data, 'visibility')
    current_wind_speed = commonFunctions.get_from_dic(json_data, 'wind', 'speed')
    current_wind_direction = commonFunctions.get_from_dic(json_data, 'wind', 'deg')
    current_clouds = commonFunctions.get_from_dic(json_data, 'clouds', 'all')
    current_sunrise = commonFunctions.get_from_dic(json_data, 'sys', 'sunrise')
    current_sunset = commonFunctions.get_from_dic(json_data, 'sys', 'sunset')  

    commonFunctions.save_temperature_data(place, current_temperature, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    commonFunctions.save_pressure_data(place, current_pressure, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    commonFunctions.save_humidity_data(place, current_humidity, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    commonFunctions.save_temperature_range_min_data(place, current_temperature_min, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    commonFunctions.save_temperature_range_max_data(place, current_temperature_max, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    commonFunctions.save_rain_data(place, current_rain, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    commonFunctions.save_visibility_data(place, current_visibility, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    commonFunctions.save_wind_data(place, current_wind_speed, current_wind_direction, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    commonFunctions.save_clouds_data(place, current_clouds, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    commonFunctions.save_sunrise_data(place, current_sunrise, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)
    commonFunctions.save_sunset_data(place, current_sunset, "FROM_UNIXTIME(%s)" % (measurement_date), creation_time)

def main():
    logging.info("Saving to file: %s" % (config.file['save_to_file']))
    logging.info("Saving to DB: %s" % (config.mysql['save_to_DB']))
    logging.info("Starting loop")
    try:
        while True:
            now = datetime.datetime.utcnow()
    
            openweathermap_jsondata = get_current_city_data()
            save_openweather_map_info_to_DB(openweathermap_jsondata, now.isoformat())

            sleep(config.open_map['sleep_time_in_seconds_between_reads'])
    except KeyboardInterrupt:
        logging.error("\nbye!")
        sys.exit(1)
    except Exception as e:
        logging.error("\nOther error occurred")
        logging.error (e)
        logging.error(traceback.format_exc())
        sys.exit(1)
    finally:
        logging.info("\nbye2!")
        #print("\nCleaning GPIO port\n")
        #GPIO.cleanup()

# call main
if __name__ == '__main__':
   main()
