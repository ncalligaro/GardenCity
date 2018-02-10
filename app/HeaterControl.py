#!/usr/bin/python
from config import config

import commonFunctions

import os
import requests
from flask import Flask, render_template, request, jsonify

from tinydb import TinyDB, Query
# import sys
# import serial
import datetime
import time
# import re
# import traceback
# import httplib
# import urllib
import json
import calendar

import threading
from multiprocessing import Process
from time import sleep
import logging

# import sys
# import RPi.GPIO as GPIO
# from lib_nrf24 import NRF24
# import spidev
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

app = Flask(__name__)

heater_is_on = False

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
    day_of_week = request.json['dayOfWeek']
    from_time = request.json['fromTime']
    to_time = request.json['toTime']
    target_temperature = request.json['targetTemperature']
    day_of_week_name = calendar.day_name[int(day_of_week)]

    if (day_of_week is not None and from_time is not None and to_time is not None and target_temperature is not None):
        new_id = schedule_table.insert({'dayOfWeek' : day_of_week, 'dayOfWeekName': day_of_week_name, 'fromTime': from_time, 'toTime': to_time, 'targetTemperature': target_temperature })
        new_schedule = schedule_table.get(doc_id=new_id)
        return jsonify(new_schedule)
    else:
        return jsonify({'errors':['One of the values was None']})

@app.route('/heater/schedule/<id>', methods=['DELETE'])
def delete_heater_schedule(id):
    schedule_table.remove(doc_ids=[int(id)])
    return ''

@app.route('/heater/status', methods=['GET'])
def get_heater_status():
    errors = []
    results = {}
    try:
        url = request.form['url']
        r = requests.get(url)
        logging.debug(r.text)
    except:
        errors.append(
            "Unable to get URL. Please make sure it's valid and try again."
        )
    return render_template('index.html', errors=errors, results=results)

def add_doc_id_as_id_to_entry(entry):
    entry['object_id'] = entry.doc_id
    return entry


def heater_controller():
    i=0
    while(True):
        sleep(1.0)
        i=i+1
        logging.debug("I'm still running: %s" % i)

def web_app():
    logging.debug("Started Webapp")
    app.run(threaded=True,debug=True, use_reloader=False)

def main():
    logging.debug("Starting loop")
    #Spawn process for webserver
    #server = Process(target=web_app)
    #t = threading.Thread(target=web_app, name='web_app')
    #t.start()
    try:
        web_app()
        #server.start()
        logging.debug("Started Process 2")
        heater_controller()
    except KeyboardInterrupt:
        logging.debug("\nbye!")
    except Exception as e:
        logging.debug("\nOther error occurred")
        logging.debug (e)
        logging.debug(traceback.format_exc())
    finally:
        #server.terminate()
        #server.join()
        #t.join()

        logging.debug("\nCleaning GPIO port\n")
        # GPIO.cleanup()


# call main
if __name__ == '__main__':    
    main()
