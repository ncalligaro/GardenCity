#!/usr/bin/python
from config import config

import commonFunctions

import os
import requests
from flask import Flask, render_template, request, jsonify

from tinydb import TinyDB, Query, where
# import serial
import datetime
import time
# import re
import traceback
# import httplib
# import urllib
import json
import calendar
from decimal import Decimal

import threading
from time import sleep
import logging

# import sys
# import RPi.GPIO as GPIO
# from lib_nrf24 import NRF24
# import spidev

logging.basicConfig(level=config.get_logging_level(),
                    format=config.runtime_variables['log_format'],
                    datefmt=config.runtime_variables['log_date_format'])

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)

boiler_status = {'is_boiler_on': False, 'is_schedule_overriden': False, 'is_temporarily_overriden': False, 'last_scheduled_value': False}


#list(calendar.day_name)
#['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
#list(calendar.day_abbr)
#['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

db = TinyDB('db.json')
schedule_table = db.table('schedules')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/heater/schedule', methods=['GET'])
def get_heater_schedule():
    schedules = schedule_table.all()
    schedules = list(map(add_doc_id_as_id_to_entry, schedules))
    schedules = sorted(schedules, key=lambda schedule: (schedule['dayOfWeek']*10000 + schedule['fromTimeDecimal']))
    return jsonify(schedules)

@app.route('/heater/schedule', methods=['POST'])
def add_heater_schedule():
    day_of_week = int(request.json['dayOfWeek'])
    from_time = request.json['fromTime']
    from_time_decimal = convert_time_to_integer(from_time)
    to_time = request.json['toTime']
    to_time_decimal = convert_time_to_integer(to_time)
    target_temperature = int(request.json['targetTemperature'])
    day_of_week_name = calendar.day_name[day_of_week]

    if (day_of_week is not None and from_time is not None and to_time is not None and target_temperature is not None):
        new_id = schedule_table.insert({'dayOfWeek' : day_of_week, 'dayOfWeekName': day_of_week_name, 'fromTime': from_time, 'fromTimeDecimal': from_time_decimal, 'toTime': to_time, 'toTimeDecimal': to_time_decimal, 'targetTemperature': target_temperature })
        new_schedule = schedule_table.get(doc_id=new_id)
        return jsonify(new_schedule)
    else:
        return jsonify({'errors':['One of the values was None']})

@app.route('/heater/schedule/<id>', methods=['DELETE'])
def delete_heater_schedule(id):
    schedule_table.remove(doc_ids=[int(id)])
    return ''

@app.route('/heater/status', methods=['PUT'])
def set_heater_status():
    boiler_status['is_boiler_on'] = request.json['isBoilerOn']
    boiler_status['is_temporarily_overriden'] = True
    boiler_status['is_schedule_overriden'] = request.json['isScheduleOverriden']
    return get_heater_status()

@app.route('/heater/status', methods=['GET'])
def get_heater_status():
    boiler_status_response = {}
    boiler_status_response['isBoilerOn'] = boiler_status['is_boiler_on']
    boiler_status_response['isScheduleOverriden'] = boiler_status['is_schedule_overriden']
    return jsonify(boiler_status_response)


@app.route('/places/<measurement_type>', methods=['GET'])
def get_places_for_type(measurement_type):
    places = commonFunctions.get_places_for_type(measurement_type)
    return jsonify(places)

@app.route('/temperature/<place>', methods=['GET'])
def get_current_temperature_for_as_json(place):
    max_age_in_mins = request.args.get('maxAge')
    return jsonify(get_current_temperature_for(place, max_age_in_mins))

def get_current_temperature_for(place, max_age_in_mins):
    temperature, measurement_date = commonFunctions.get_last_measurement_for_place(commonFunctions.MEASUREMENT_TYPE_TEMPERATURE, place, max_age_in_mins)
    result = {}
    result['temperature'] = temperature
    result['measurement_date'] = measurement_date
    return result


def add_doc_id_as_id_to_entry(entry):
    entry['object_id'] = entry.doc_id
    return entry

def get_boiler_text_value_for(value):
    if value:
        return 'on'
    return 'off'

def get_active_schedule_configuration():
    now = datetime.datetime.now()
    today_day_of_week = now.weekday()
    current_integer_time = convert_time_to_integer("%s:%s" % (now.hour, now.minute))
    active_schedules = schedule_table.search((where('dayOfWeek') == today_day_of_week) & (where('fromTimeDecimal') <= current_integer_time) & (where('toTimeDecimal') > current_integer_time))
    if not active_schedules:
        logging.debug('There was no active schedule')
        return None
    if len(active_schedules) > 1:
        logging.error('More than one active schedule found for %s. Active Schedules are:' % now.isoformat())
        for active_schedule in active_schedules:
            logging.error('dayOfWeek: %s | fromTime: %s | toTime: %s' % (active_schedule['dayOfWeek'], active_schedule['fromTime'], active_schedule['toTime']))
        raise ValueError('More than one active schedule found for %s' % now.isoformat())
    logging.debug('Found an active schedule')
    return active_schedules[0]

def get_boiler_status_for_active_schedule():
    today_schedules = get_active_schedule_configuration()
    return today_schedules is not None

def convert_time_to_integer(time_record):
    (h, m) = time_record.split(':')
    return int(h)*100 + int(m)
    
def calculate_new_boiler_state_on_schedule():
    state = True
    reason = '0'
    reason_explanation = 'Unknown reason'
    logging.debug("Calculating new boiler state")

    # If it is fully overriden then return current value
    if boiler_status['is_schedule_overriden']:
        state = boiler_status['is_boiler_on']
        reason = '1'
        reason_explanation = 'Schedule overriden. Returned current value'
        logging.debug("%s. Value is %s " % (reason_explanation, state))
        return state, reason, reason_explanation

    # If it is NOT fully overriden then it might be temporarily overriden
    scheduled_boiler_status = get_boiler_status_for_active_schedule()
    if boiler_status['is_temporarily_overriden']:
        if boiler_status['last_scheduled_value'] != scheduled_boiler_status:
            # Last boiler status is not the same as the new one and it is temporarily overriden so change it!
            boiler_status['last_scheduled_value'] = scheduled_boiler_status
            boiler_status['is_temporarily_overriden'] = False
            state = scheduled_boiler_status
            reason = '2'
            reason_explanation = 'Schedule temporarily overriden but scheduled value changed. Returned new value'
            logging.debug("%s. Value is %s " % (reason_explanation, state))
            return state, reason, reason_explanation
        # Last boiler status is the same so lets keep the current value because it is temporarily overriden
        state = boiler_status['is_boiler_on']
        reason = '3'
        reason_explanation = 'Schedule temporarily overriden but scheduled value has not changed. Returned previous value'
        logging.debug("%s. Value is %s " % (reason_explanation, state))
        return state, reason, reason_explanation

    # There was no override so lets follow the schedule
    state = scheduled_boiler_status
    boiler_status['last_scheduled_value'] = scheduled_boiler_status
    reason = '4'
    reason_explanation = 'Following schedule. Returned schedule value %s' % scheduled_boiler_status
    logging.debug("%s. Value is %s " % (reason_explanation, state))
    return state, reason, reason_explanation

def calculate_new_boiler_state_on_temperature():
    current_temperature_dining = get_current_temperature_for('Dining', 15)
    if current_temperature_dining is None:
        logging.error('Unable to read Dining temperature')
        return None, None, None
    
    current_schedule = get_active_schedule_configuration()
    if not current_schedule:
        logging.debug('There is no schedule active at this moment. Setting boiler to off/False')
        return False, '.1', 'There is no schedule active at this moment. Boiler needs to be off'

    temperature = current_temperature_dining['temperature']
    if is_temperature_within_margin(current_schedule['targetTemperature'], config.boiler['temperature_margin'], temperature):
        return True, '.2', 'Temperature within margin. Boiler needs to be on'
    return False, '.3', 'Temperature is too high. Boiler needs to be off'

def is_temperature_within_margin(target_temperature, margin, current_temperature):
    difference = target_temperature - current_temperature
    is_too_low = current_temperature < target_temperature
    is_within_margin = abs(difference) < margin
    result = is_too_low or is_within_margin
    logging.debug('current_temperature: %s | target_temperature: %s' % (current_temperature, target_temperature))
    logging.debug('temperature is too low: %s | temperature is within margin: %s (diff is %s) | result: %s' % (is_too_low, is_within_margin, difference, result))
    return result

def calculate_new_boiler_state():
    # First calculate schedule state
    schedule_state, schedule_reason, schedule_reason_explanation = calculate_new_boiler_state_on_schedule()
    logging.debug('schedule_state: %s | schedule_reason: %s | schedule_reason_explanation: %s' % (schedule_state, schedule_reason, schedule_reason_explanation))
    # Now calculate temperature state
    temperature_state, temperature_reason, temperature_reason_explanation = calculate_new_boiler_state_on_temperature()
    logging.debug('temperature_state: %s | temperature_reason: %s | temperature_reason_explanation: %s' % (temperature_state, temperature_reason, temperature_reason_explanation))
    logging.debug('New state should be %s' % (schedule_state and temperature_state))
    return schedule_state and temperature_state, '%s%s' % (schedule_reason, temperature_reason), '%s - %s' % (schedule_reason_explanation, temperature_reason_explanation)

def heater_controller_daemon():
    logging.info("Starting Heater Controller Daemon")
    while(True):
        state, reason, reason_explanation = calculate_new_boiler_state()
        state_text = get_boiler_text_value_for(state)

        now = datetime.datetime.utcnow()

        commonFunctions.save_heater_data(state_text, reason, reason_explanation, now.isoformat(), now.isoformat())
        boiler_status['is_boiler_on'] = state
        logging.debug("is_boiler_on: %s | is_schedule_overriden: %s | is_temporarily_overriden: %s | last_scheduled_value: %s" % (boiler_status['is_boiler_on'], boiler_status['is_schedule_overriden'], boiler_status['is_temporarily_overriden'], boiler_status['last_scheduled_value']))
        sleep(config.boiler['sleep_time_in_seconds_between_checks'])

def web_app_main():
    logging.info("Starting webapp")
    debug = logging.getLogger().isEnabledFor(logging.DEBUG)
    if not debug:
        log_flask = logging.getLogger('werkzeug')
        log_flask.setLevel(logging.ERROR)
    app.run(debug=debug, use_reloader=False, host=config.webapp['listening_ip'])

def main():
    try:
        logging.info("Saving to file: %s" % (config.file['save_to_file']))
        logging.info("Saving to DB: %s" % (config.mysql['save_to_DB']))
        t = threading.Thread(name='web_app_main',target=web_app_main)
        t.setDaemon(True)
        t.start()
        heater_controller_daemon()
    except KeyboardInterrupt:
        logging.debug("bye!")
    except Exception as e:
        logging.debug("Other error occurred")
        logging.debug (e)
        logging.debug(traceback.format_exc())
    finally:
        #logging.debug("\nCleaning GPIO port\n")
        # GPIO.cleanup()
        logging.info("Shutting Down")

# call main
if __name__ == '__main__':    
    main()
