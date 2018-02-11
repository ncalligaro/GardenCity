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
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',
                    datefmt='%H:%M:%S')

app = Flask(__name__)

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
    schedules = sorted(schedules, key=lambda schedule: schedule['dayOfWeek'])
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

def add_doc_id_as_id_to_entry(entry):
    entry['object_id'] = entry.doc_id
    return entry

def get_boiler_text_value_for(value):
    if value:
        return 'on'
    return 'off'

def get_scheduled_boiler_status():
    now = datetime.datetime.now()
    today_day_of_week = now.weekday()
    current_integer_time = convert_time_to_integer("%s:%s" % (now.hour, now.minute))
    #schedule_query = Query()
    #schedule_table.search(schedule_query.dayOfWeek.test(test_func, 0, 21))
    todays_schedules = schedule_table.search((where('dayOfWeek') == today_day_of_week) & (where('fromTimeDecimal') <= current_integer_time) & (where('toTimeDecimal') > current_integer_time))
    #todays_schedules = schedule_table.search((where('fromTimeDecimal') <= current_integer_time) & (where('toTimeDecimal') > current_integer_time))
    #logging.debug(jsonify(todays_schedules))
    return not not todays_schedules


def convert_time_to_integer(time_record):
    (h, m) = time_record.split(':')
    return int(h)*100 + int(m)
    
# def isHourBetween(val, min, max):
#     return min <= val < max

def calculate_new_boiler_state():
    state = {}
    state['is_boiler_on'] = True
    reason = '0'
    reason_explanation = 'Unknown reason'
    logging.debug("Calculating new boiler state")

    # If it is fully overriden then return current value
    if boiler_status['is_schedule_overriden']:
        state['is_boiler_on'] = boiler_status['is_boiler_on']
        reason = '1'
        reason_explanation = 'Schedule overriden. Returned current value'
        logging.debug("%s. Value is %s " % (reason_explanation, state['is_boiler_on']))
        return state, reason, reason_explanation

    # If it is NOT fully overriden then it might be temporarily overriden
    scheduled_boiler_status = get_scheduled_boiler_status()
    if boiler_status['is_temporarily_overriden']:
        if boiler_status['last_scheduled_value'] != scheduled_boiler_status:
            # Last boiler status is not the same as the new one and it is temporarily overriden so change it!
            boiler_status['last_scheduled_value'] = scheduled_boiler_status
            boiler_status['is_temporarily_overriden'] = False
            state['is_boiler_on'] = scheduled_boiler_status
            reason = '2'
            reason_explanation = 'Schedule temporarily overriden but scheduled value changed. Returned new value'
            logging.debug("%s. Value is %s " % (reason_explanation, state['is_boiler_on']))
            return state, reason, reason_explanation
        # Last boiler status is the same so lets keep the current value because it is temporarily overriden
        state['is_boiler_on'] = boiler_status['is_boiler_on']
        reason = '3'
        reason_explanation = 'Schedule temporarily overriden but scheduled value has not changed. Returned previous value'
        logging.debug("%s. Value is %s " % (reason_explanation, state['is_boiler_on']))
        return state, reason, reason_explanation

    # There was no override so lets follow the schedule
    state['is_boiler_on'] = scheduled_boiler_status
    boiler_status['last_scheduled_value'] = scheduled_boiler_status
    reason = '4'
    reason_explanation = 'Following schedule. Returned schedule''s value'
    logging.debug("%s. Value is %s " % (reason_explanation, state['is_boiler_on']))
    return state, reason, reason_explanation

def heater_controller_daemon():
    logging.debug("Starting Heater Controller Daemon")
    while(True):
        state, reason, reason_explanation = calculate_new_boiler_state()
        state['text_value'] = get_boiler_text_value_for(state['is_boiler_on'])

        now = datetime.datetime.utcnow()

        #commonFunctions.save_heater_data(state['text_value'], reason, reason_explanation, now.isoformat(), now.isoformat()):
        boiler_status['is_boiler_on'] = state['is_boiler_on']
        logging.debug("is_boiler_on: %s | is_schedule_overriden: %s | is_temporarily_overriden: %s | last_scheduled_value: %s" % (boiler_status['is_boiler_on'], boiler_status['is_schedule_overriden'], boiler_status['is_temporarily_overriden'], boiler_status['last_scheduled_value']))
        sleep(5.0)

def web_app_main():
    logging.debug("Starting webapp")
    debug = logging.getLogger().isEnabledFor(logging.DEBUG)
    app.run(debug=debug, use_reloader=False, host="0.0.0.0")

def main():
    try:
        commonFunctions.error_print("Saving to file: %s" % (config.file['save_to_file']))
        commonFunctions.error_print("Saving to DB: %s" % (config.mysql['save_to_DB']))
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
        logging.debug("Shutting Down")

# call main
if __name__ == '__main__':    
    main()
