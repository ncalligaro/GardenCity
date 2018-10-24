#!/usr/bin/python
from config import config

import commonFunctions

import datetime
from time import sleep
import traceback
import logging

import sys
import RPi.GPIO as GPIO

#Import sensors conditionally depending on selected modules
for sensor in config.local_sensors['sensors']:
    sensor_model = sensor['sensor_model']
    if sensor_model == 'DHT22' or sensor_model == 'DHT11':
        import Adafruit_DHT
    if sensor_model == 'DS18B20':
        from w1thermsensor import W1ThermSensor


logging.basicConfig(level=config.get_logging_level(),
                    format=config.runtime_variables['log_format'],
                    datefmt=config.runtime_variables['log_date_format'])

GPIO.setmode(GPIO.BCM)

recent_values = {}
recent_values['humidity'] = []
recent_values['temperature'] = []
number_of_values_to_average = 5
#max_variation_in_units = 9

def get_local_sensor_data(sensor_config):
    sensor_model = sensor_config['sensor_model']
    RH, T = None, None
    if sensor_model == 'DHT22':
        RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, sensor_config['gpio_port'])
    if sensor_model == 'DHT11':
        RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, sensor_config['gpio_port'])
    if sensor_model == 'DS18B20':
        sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_config['id'])
        RH, T = None, sensor.get_temperature()

    if RH is not None and T is not None:
        return (str(RH), str(T))
    
    if RH is not None and T is None:
        return (str(RH), None)
    
    if RH is None and T is not None:
        return (None, str(T))

    return None, None

def is_within_range(type, value, sensor_config):
    global recent_values
    if len(recent_values[type]) < number_of_values_to_average:
        logging.info("There are less than %s values for %s. Adding %s to list" % (number_of_values_to_average, type, value))
        return True

    logging.info("Average of array for type %s is %s" % (type, sum(recent_values[type])/len(recent_values[type])))
    max_value = sum(recent_values[type])/len(recent_values[type]) + sensor_config['variation_margin_units']
    min_value = sum(recent_values[type])/len(recent_values[type]) - sensor_config['variation_margin_units']
    if min_value < value < max_value:
        logging.debug("There are more than %s values for %s. Value %s was within range" % (number_of_values_to_average, type, value))
        return True

    logging.info("Measure of %s %s was not within range. Ignoring value" % (type, value))
    return False

def update_recent_list(type, value):
    global recent_values
    if len(recent_values[type]) < number_of_values_to_average:
        recent_values[type].append(value)
    else:
        recent_values[type] = recent_values[type][1:]
        recent_values[type].append(value)
    logging.info("New len of array for type %s is %s" % (type, len(recent_values[type])))

def main():
    logging.info("Saving to file: %s" % (config.file['save_to_file']))
    logging.info("Saving to DB: %s" % (config.mysql['save_to_DB']))
    logging.info("Starting loop")
    try:
        while True:
            for sensor in config.local_sensors['sensors']:
                now = datetime.datetime.utcnow()

                LRH, LT = get_local_sensor_data(sensor)

                if LRH is not None and is_within_range('humidity', float(LRH), sensor):
                    commonFunctions.save_humidity_data(sensor['location_name'], LRH, now.isoformat(), now.isoformat())
                    update_recent_list('humidity', float(LRH))
                if LT is not None and is_within_range('temperature', float(LT), sensor):
                    commonFunctions.save_temperature_data(sensor['location_name'], LT, now.isoformat(), now.isoformat())
                    update_recent_list('temperature', float(LT))

            sleep(config.local_sensors['sleep_time_in_seconds_between_reads'])
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
