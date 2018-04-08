#!/usr/bin/python
from config import config

import commonFunctions
import configFunctions

import os
import requests
from flask import Flask, render_template, request, jsonify, Response, session
import flask

from functools import wraps

from tinydb import TinyDB, Query, where
from datetime import datetime
from datetime import timedelta 
import pytz

import time

import traceback

import json
import calendar
from decimal import Decimal

import threading
from time import sleep
import logging

import sys
import RPi.GPIO as GPIO

import google.oauth2.credentials
import google_auth_oauthlib.flow

# from lib_nrf24 import NRF24
# import spidev
# import serial
# import re
# import httplib
# import urllib

logging.basicConfig(level=config.get_logging_level(),
                    format=config.runtime_variables['log_format'],
                    datefmt=config.runtime_variables['log_date_format'])

GPIO.setmode(GPIO.BCM)

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)
app.secret_key = configFunctions.get_client_secret()

SCOPES = ['email', 'openid']

#Keys
IS_SYSTEM_ON_KEY = 'is_system_on'
IS_SYSTEM_ON_JSON_KEY = 'isSystemOn'
IS_BOILER_ON_KEY = 'is_boiler_on'
IS_BOILER_ON_JSON_KEY = 'isBoilerOn'
TEMPERATURE_MARGIN_KEY = 'temperature_margin'
BOILER_STATUS_KEY = 'boiler_status'

IS_CURRENT_SCHEDULE_OVERRIDEN_KEY = 'is_current_schedule_overriden'
IS_CURRENT_SCHEDULE_OVERRRIDEN_JSON_KEY = 'isCurrentScheduleOverriden'
LAST_SCHEDULED_VALUE_KEY = 'last_scheduled_value'
SCHEDULE_OVERRIDEN_TIME_KEY = 'schedule_overriden_time'
SCHEDULE_OVERRIDEN_TIME_JSON_KEY = 'scheduleOverridenTime'
SCHEDULE_OVERRIDEN_STARTED_KEY = 'schedule_overriden_started'
SCHEDULE_OVERRIDEN_STARTED_JSON_KEY = 'scheduleOverridenStarted'
ALLOWED_LOGINS_KEY = 'allowed_logins'

MAINTAIN_TEMPERATURE_KEY = 'maintain_temperature'
MAINTAIN_TEMPERATURE_JSON_KEY = 'maintainTemperature'
MANUAL_TEMPERATURE_KEY = 'manual_temperature'
MANUAL_TEMPERATURE_JSON_KEY = 'manualTemperature'
MANUAL_LOCATION_KEY = 'manual_location'
MANUAL_LOCATION_JSON_KEY = 'manualLocation'

DAY_OF_WEEK_JSON_KEY = 'dayOfWeek'
FROM_TIME_JSON_KEY = 'fromTime'
FROM_TIME_DECIMAL_JSON_KEY = 'fromTimeDecimal'
TO_TIME_JSON_KEY = 'toTime'
TO_TIME_DECIMAL_JSON_KEY = 'toTimeDecimal'
TARGET_TEMPERATURE_JSON_KEY = 'targetTemperature'
TARGET_PLACE_JSON_KEY = 'targetPlace'
DAY_OF_WEEK_NAME_JSON_KEY = 'dayOfWeekName'

MODE_KEY = 'system_mode'
MODE_JSON_KEY = 'mode'

MAX_AGE_JSON_KEY = 'maxAge'

SESSION_CREDENTIALS_KEY = 'credentials'
SESSION_USER_DATA_KEY = 'user_data'
#list(calendar.day_name)
#['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
#list(calendar.day_abbr)
#['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

#db = TinyDB('db.json')
#schedule_table = db.table('schedules')
schedule_table = configFunctions.get_schedule_table()
runtime_config = configFunctions.get_runtime_config()

def requires_user_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if SESSION_CREDENTIALS_KEY not in flask.session:
            logging.debug("User session not initiated")
            return authorize()
        if flask.session[SESSION_USER_DATA_KEY]['email'] not in runtime_config[ALLOWED_LOGINS_KEY]:
            logging.debug("User %s not allowed" % flask.session[SESSION_USER_DATA_KEY]['email'])
            return user_unathorized()
        logging.debug("User %s is allowed" % flask.session[SESSION_USER_DATA_KEY]['email'])
        return f(*args, **kwargs)
    return decorated

def user_unathorized():
    return Response(
    'Your google email is not authorized.</br>\n'
    'You have to login with proper credentials</br>\n'
    '<a href="/logout">Click here</a> to close your session ', 401)

def unathorized():
    return Response(
    'Your google email is not authorized.\n'
    'You have to login with proper credentials', 401)

def requires_service_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if SESSION_CREDENTIALS_KEY not in flask.session:
            logging.debug("User session not initiated")
            return unathorized()
        if flask.session[SESSION_USER_DATA_KEY]['email'] not in runtime_config[ALLOWED_LOGINS_KEY]:
            logging.debug("User %s not allowed" % flask.session[SESSION_USER_DATA_KEY]['email'])
            return unathorized()
        logging.debug("User %s is allowed" % flask.session[SESSION_USER_DATA_KEY]['email'])
        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET'])
@requires_user_auth
def index():
    return render_template('index.html')

@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  logging.debug("Initiating user authentication")
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      configFunctions.CLIENT_SECRETS_FILE, scopes=SCOPES)

  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state
  return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      configFunctions.CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)
  
  google_session = flow.authorized_session()
  #print google_session.get('https://www.googleapis.com/userinfo/v2/me').json()
  flask.session[SESSION_USER_DATA_KEY] = google_session.get('https://www.googleapis.com/userinfo/v2/me').json()

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session[SESSION_CREDENTIALS_KEY] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('index'))

@app.route('/logout')
def logout():
    revoke()
    clear_credentials()
    return flask.redirect(flask.url_for('logout_success'))    

@app.route('/logoutSuccess')
def logout_success():
    return 'Logout Success</br><a href="/">Click here</a> to login again'

@app.route('/revoke')
def revoke():
  if SESSION_CREDENTIALS_KEY not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session[SESSION_CREDENTIALS_KEY])

  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.')
  else:
    return('An error occurred.')


@app.route('/clear')
@requires_user_auth
def clear_credentials():
    if SESSION_CREDENTIALS_KEY in flask.session:
        del flask.session[SESSION_CREDENTIALS_KEY]
    if SESSION_USER_DATA_KEY in flask.session:
        del flask.session[SESSION_USER_DATA_KEY]
    return ('Credentials have been cleared.<br><br>')

@app.route('/user', methods=['GET'])
@requires_service_auth
def get_user():
    logging.debug(flask.session[SESSION_USER_DATA_KEY])
    return jsonify(flask.session[SESSION_USER_DATA_KEY])

@app.route('/schedule', methods=['GET'])
@requires_service_auth
def get_heater_schedule():
    schedules = schedule_table.all()
    schedules = list(map(add_doc_id_as_id_to_entry, schedules))
    schedules = sorted(schedules, key=lambda schedule: (schedule[DAY_OF_WEEK_JSON_KEY]*10000 + schedule[FROM_TIME_DECIMAL_JSON_KEY]))
    return jsonify(schedules)

@app.route('/schedule', methods=['POST'])
@requires_service_auth
def add_heater_schedule():
    day_of_week = int(request.json[DAY_OF_WEEK_JSON_KEY])
    from_time = request.json[FROM_TIME_JSON_KEY]
    from_time_decimal = convert_time_to_integer(from_time)
    to_time = request.json[TO_TIME_JSON_KEY]
    to_time_decimal = convert_time_to_integer(to_time)
    #BUG here, the DB cannot handle json of decimals to save them but it can read them (shrug)
    target_temperature = float(request.json[TARGET_TEMPERATURE_JSON_KEY])
    target_place = request.json[TARGET_PLACE_JSON_KEY]
    day_of_week_name = calendar.day_name[day_of_week]

    if (day_of_week is not None and from_time is not None and to_time is not None and target_temperature is not None):
        new_id = schedule_table.insert({DAY_OF_WEEK_JSON_KEY : day_of_week, DAY_OF_WEEK_NAME_JSON_KEY: day_of_week_name, FROM_TIME_JSON_KEY: from_time, FROM_TIME_DECIMAL_JSON_KEY: from_time_decimal, TO_TIME_JSON_KEY: to_time, TO_TIME_DECIMAL_JSON_KEY: to_time_decimal, TARGET_TEMPERATURE_JSON_KEY: target_temperature, TARGET_PLACE_JSON_KEY: target_place })
        new_schedule = schedule_table.get(doc_id=new_id)
        return jsonify(new_schedule)
    else:
        return jsonify({'errors':['One of the values was None']})

@app.route('/schedule/<id>', methods=['DELETE'])
@requires_service_auth
def delete_heater_schedule(id):
    schedule_table.remove(doc_ids=[int(id)])
    return ''

@app.route('/heater/status', methods=['PUT'])
@requires_service_auth
def set_heater_status():
    #runtime_config[BOILER_STATUS_KEY][IS_BOILER_ON_KEY] = request.json[IS_BOILER_ON_JSON_KEY]
    global runtime_config
    runtime_config[IS_SYSTEM_ON_KEY] = request.json[IS_SYSTEM_ON_JSON_KEY]
    runtime_config[BOILER_STATUS_KEY][MAINTAIN_TEMPERATURE_KEY] = request.json[MAINTAIN_TEMPERATURE_JSON_KEY]
    runtime_config[BOILER_STATUS_KEY][MANUAL_TEMPERATURE_KEY] = request.json[MANUAL_TEMPERATURE_JSON_KEY]
    runtime_config[BOILER_STATUS_KEY][MANUAL_LOCATION_KEY] = request.json[MANUAL_LOCATION_JSON_KEY]
    runtime_config[BOILER_STATUS_KEY][IS_CURRENT_SCHEDULE_OVERRIDEN_KEY] = request.json[IS_CURRENT_SCHEDULE_OVERRRIDEN_JSON_KEY]
    #runtime_config[BOILER_STATUS_KEY][SCHEDULE_OVERRIDEN_STARTED_KEY] = request.json[SCHEDULE_OVERRIDEN_STARTED_JSON_KEY]
    runtime_config[BOILER_STATUS_KEY][SCHEDULE_OVERRIDEN_TIME_KEY] = request.json[SCHEDULE_OVERRIDEN_TIME_JSON_KEY]

    #runtime_config[BOILER_STATUS_KEY][LAST_SCHEDULED_VALUE_KEY] = runtime_config[BOILER_STATUS_KEY][IS_BOILER_ON_KEY]
    
    runtime_config = configFunctions.save_runtime_config(runtime_config)

    heater_controller_actioner()
    return ''

@app.route('/heater/overridenDate', methods=['PUT'])
@requires_service_auth
def set_heater_overridenDate():
    global runtime_config
    runtime_config[BOILER_STATUS_KEY][SCHEDULE_OVERRIDEN_STARTED_KEY] = request.json[SCHEDULE_OVERRIDEN_STARTED_JSON_KEY]    
    runtime_config = configFunctions.save_runtime_config(runtime_config)

    heater_controller_actioner()
    return ''

@app.route('/heater/status', methods=['GET'])
@requires_service_auth
def get_heater_status():
    heater_controller_actioner()

    boiler_status_response = {}
    boiler_status_response[IS_SYSTEM_ON_JSON_KEY] = runtime_config[IS_SYSTEM_ON_KEY]
    boiler_status_response[IS_BOILER_ON_JSON_KEY] = runtime_config[BOILER_STATUS_KEY][IS_BOILER_ON_KEY]
    boiler_status_response[MAINTAIN_TEMPERATURE_JSON_KEY] = runtime_config[BOILER_STATUS_KEY][MAINTAIN_TEMPERATURE_KEY]
    boiler_status_response[MANUAL_TEMPERATURE_JSON_KEY] = runtime_config[BOILER_STATUS_KEY][MANUAL_TEMPERATURE_KEY]
    boiler_status_response[MANUAL_LOCATION_JSON_KEY] = runtime_config[BOILER_STATUS_KEY][MANUAL_LOCATION_KEY]
    boiler_status_response[SCHEDULE_OVERRIDEN_STARTED_JSON_KEY] = runtime_config[BOILER_STATUS_KEY][SCHEDULE_OVERRIDEN_STARTED_KEY]
    boiler_status_response[SCHEDULE_OVERRIDEN_TIME_JSON_KEY] = runtime_config[BOILER_STATUS_KEY][SCHEDULE_OVERRIDEN_TIME_KEY]
    boiler_status_response[IS_CURRENT_SCHEDULE_OVERRRIDEN_JSON_KEY] = runtime_config[BOILER_STATUS_KEY][IS_CURRENT_SCHEDULE_OVERRIDEN_KEY]
    return jsonify(boiler_status_response)

@app.route('/system/status', methods=['GET'])
@requires_service_auth
def get_system_statys():
    isSystemOn = {}
    isSystemOn[IS_SYSTEM_ON_JSON_KEY] = runtime_config[IS_SYSTEM_ON_KEY]
    return jsonify(isSystemOn)

@app.route('/system/status', methods=['POST'])
@requires_service_auth
def set_system_status():
    global runtime_config
    runtime_config[IS_SYSTEM_ON_KEY] = request.json[IS_SYSTEM_ON_JSON_KEY]
    runtime_config = configFunctions.save_runtime_config(runtime_config)
    return ''

@app.route('/system/mode', methods=['GET'])
@requires_service_auth
def get_system_mode():
    mode = {}
    mode[MODE_JSON_KEY] = runtime_config[MODE_KEY]
    return jsonify(mode)

@app.route('/system/mode', methods=['POST'])
@requires_service_auth
def set_system_mode():
    global runtime_config
    runtime_config[MODE_KEY] = request.json[MODE_JSON_KEY]
    runtime_config = configFunctions.save_runtime_config(runtime_config)
    return ''

@app.route('/places/<measurement_type>', methods=['GET'])
@requires_service_auth
def get_places_for_type(measurement_type):
    places = commonFunctions.get_places_for_type(measurement_type)
    #places = runtime_config['available_places']
    return jsonify(places)

@app.route('/temperature/avg/<place>', methods=['GET'])
@requires_service_auth
def get_current_avg_temperature_for_as_json(place):
    max_age_in_mins = request.args.get(MAX_AGE_JSON_KEY)
    return jsonify(get_current_avg_temperature_for(place, max_age_in_mins))

def get_current_avg_temperature_for(place, time_period_in_mins):
    temperature, measurement_date = commonFunctions.get_last_avg_measurement_for_place(commonFunctions.MEASUREMENT_TYPE_TEMPERATURE, place, time_period_in_mins)
    result = {}
    result['temperature'] = temperature
    result['measurement_date'] = measurement_date
    return result

@app.route('/temperature/<place>', methods=['GET'])
@requires_service_auth
def get_current_temperature_for_as_json(place):
    max_age_in_mins = request.args.get(MAX_AGE_JSON_KEY)
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

@app.route('/schedule/active', methods=['GET'])
@requires_service_auth
def get_active_schedule_configuration_as_json():
    return jsonify(get_active_schedule_configuration())

def get_active_schedule_configuration():
    now = datetime.now()
    today_day_of_week = now.weekday()
    current_integer_time = convert_time_to_integer("%s:%s" % (now.hour, now.minute))
    active_schedules = schedule_table.search((where(DAY_OF_WEEK_JSON_KEY) == today_day_of_week) & (where(FROM_TIME_DECIMAL_JSON_KEY) <= current_integer_time) & (where(TO_TIME_DECIMAL_JSON_KEY) > current_integer_time))
    if not active_schedules:
        logging.debug('There was no active schedule')
        return None
    if len(active_schedules) > 1:
        logging.error('More than one active schedule found for %s. Active Schedules are:' % now.isoformat())
        for active_schedule in active_schedules:
            logging.error('dayOfWeek: %s | fromTime: %s | toTime: %s' % (active_schedule[DAY_OF_WEEK_JSON_KEY], active_schedule[FROM_TIME_JSON_KEY], active_schedule[TO_TIME_JSON_KEY]))
        raise ValueError('More than one active schedule found for %s' % now.isoformat())
    logging.debug('Found an active schedule: %s', active_schedules[0])
    return active_schedules[0]

def get_boiler_status_for_active_schedule():
    today_schedules = get_active_schedule_configuration()
    return today_schedules is not None

def convert_time_to_integer(time_record):
    (h, m) = time_record.split(':')
    return int(h)*100 + int(m)
    
def is_system_in_manual_mode():
    return runtime_config['system_mode'] == 'manual'

def is_system_in_schedule_mode():
    return runtime_config['system_mode'] == 'schedule'

def is_schedule_overriden_temporarily():
    global runtime_config
    if not runtime_config[BOILER_STATUS_KEY][IS_CURRENT_SCHEDULE_OVERRIDEN_KEY]:
        logging.debug("Schedule was not overriden")
        return False
    started_timestamp = runtime_config[BOILER_STATUS_KEY][SCHEDULE_OVERRIDEN_STARTED_KEY]
    if (not started_timestamp):
        logging.debug("Schedule Overriden Started date is not defined. Schedule was not overriden")
        return False
    # javascript timestamp is in millis, and python one is not
    started_timestamp = started_timestamp / 1000
    hours = runtime_config[BOILER_STATUS_KEY][SCHEDULE_OVERRIDEN_TIME_KEY]
    if not hours:
        logging.debug("Schedule Overriden Time was not defined. Schedule was not overriden")
        return False

    end_date = datetime.fromtimestamp(started_timestamp, tz=pytz.utc) + timedelta(hours=hours)
    now = datetime.utcnow()
    now = now.replace(tzinfo=pytz.utc) 
    logging.debug("Schedule override end date is %s and now is %s" % (end_date, now))
    if (now >= end_date):
        #Clear flag
        logging.debug("Schedule Override already finished. Removing flag")
        runtime_config[BOILER_STATUS_KEY][IS_CURRENT_SCHEDULE_OVERRIDEN_KEY] = False
        runtime_config[BOILER_STATUS_KEY][SCHEDULE_OVERRIDEN_STARTED_KEY] = None
        runtime_config[BOILER_STATUS_KEY][SCHEDULE_OVERRIDEN_TIME_KEY] = 1.5
        runtime_config = configFunctions.save_runtime_config(runtime_config)
        #TODO: problem with this approach is that it make take a minute to refresh the UI in web page
        # It should be catered by the fact that the start date is only updated when the currentScheduleOverriden flag is updated
        return False
    else:
        logging.debug("Schedule is overriden")
        return True

def calculate_new_boiler_state_on_selected_mode():
    # Reason 5 is system is off
    state = True
    reason = '0'
    reason_explanation = 'Unknown reason'
    logging.debug("Calculating new boiler state")

    if is_system_in_manual_mode():
        state = runtime_config[BOILER_STATUS_KEY][MAINTAIN_TEMPERATURE_KEY]
        reason = '6'
        reason_explanation = 'Manual mode, returning mantainTemperature value %s' % state
        logging.debug("%s. Value is %s " % (reason_explanation, state))
        return state, reason, reason_explanation

    if is_system_in_schedule_mode(): 
        if is_schedule_overriden_temporarily():
            state = runtime_config[BOILER_STATUS_KEY][MAINTAIN_TEMPERATURE_KEY]
            reason = '1'
            reason_explanation = 'Schedule overriden. returning mantainTemperature value %s' % state
            logging.debug("%s. Value is %s " % (reason_explanation, state))
            return state, reason, reason_explanation

        scheduled_boiler_status = get_boiler_status_for_active_schedule()
        if runtime_config[BOILER_STATUS_KEY][IS_CURRENT_SCHEDULE_OVERRIDEN_KEY]:
            if runtime_config[BOILER_STATUS_KEY][LAST_SCHEDULED_VALUE_KEY] != scheduled_boiler_status:
                # Last boiler status is not the same as the new one and it is temporarily overriden so change it!
                runtime_config[BOILER_STATUS_KEY][LAST_SCHEDULED_VALUE_KEY] = scheduled_boiler_status
                runtime_config[BOILER_STATUS_KEY][IS_CURRENT_SCHEDULE_OVERRIDEN_KEY] = False
                state = scheduled_boiler_status
                reason = '2'
                reason_explanation = 'Schedule temporarily overriden but scheduled value changed. Returned new value'
                logging.debug("%s. Value is %s " % (reason_explanation, state))
                return state, reason, reason_explanation
            # Last boiler status is the same so lets keep the current value because it is temporarily overriden
            state = runtime_config[BOILER_STATUS_KEY][IS_BOILER_ON_KEY]
            reason = '3'
            reason_explanation = 'Schedule temporarily overriden but scheduled value has not changed. Returned previous value'
            logging.debug("%s. Value is %s " % (reason_explanation, state))
            return state, reason, reason_explanation

        # There was no override so lets follow the schedule
        state = scheduled_boiler_status
        runtime_config[BOILER_STATUS_KEY][LAST_SCHEDULED_VALUE_KEY] = scheduled_boiler_status
        reason = '4'
        reason_explanation = 'Following schedule. Returned schedule value %s' % scheduled_boiler_status
        logging.debug("%s. Value is %s " % (reason_explanation, state))
        return state, reason, reason_explanation

def calculate_new_boiler_state_on_temperature(is_boiler_on):
    avg_time_period_mins = 5
    #Set default location
    location = runtime_config[BOILER_STATUS_KEY][MANUAL_LOCATION_KEY]
    current_schedule = get_active_schedule_configuration()
    if current_schedule:
        if is_schedule_overriden_temporarily():
            logging.debug("Location temporarily overriden")
            location = runtime_config[BOILER_STATUS_KEY][MANUAL_LOCATION_KEY]
        else:
            logging.debug("Using schedule location")
            location = current_schedule[TARGET_PLACE_JSON_KEY]

    current_avg_temperature_on_selected_location = get_current_avg_temperature_for(location, avg_time_period_mins)
    logging.debug('average temperature past %s minutes in %s is %s' % (avg_time_period_mins, location, current_avg_temperature_on_selected_location))
    
    if current_avg_temperature_on_selected_location is None:
        location = runtime_config[MANUAL_LOCATION_KEY]
        current_avg_temperature_on_selected_location = get_current_avg_temperature_for(location, avg_time_period_mins)
        logging.debug("Unable to use schedule for selected location. Falling back to default %s" % location)
        logging.debug('average temperature past %s minutes in %s is %s' % (avg_time_period_mins, location, current_avg_temperature_on_selected_location))
    
    #Temp is still none, what the hell?
    if current_avg_temperature_on_selected_location is None:
        logging.error('Unable to read avg %s temperature' % location)
        return False, '.7', ('Unable to read avg %s temperature' % location)
    
    temperature = current_avg_temperature_on_selected_location['temperature']
    if temperature is None:
        logging.error('Unable to read %s temperature' % location)
        return False, '.6', ('Unable to read %s temperature' % location)
        
    if is_system_in_manual_mode() or (is_system_in_schedule_mode() and is_schedule_overriden_temporarily()):
        if is_system_in_manual_mode():
            logging.debug('System in manual mode at this moment. Using manual temperature %s' % (runtime_config[BOILER_STATUS_KEY][MANUAL_TEMPERATURE_KEY]))
        else:
            logging.debug('System in schedule mode but temporarily overriden. Using manual temperature %s' % (runtime_config[BOILER_STATUS_KEY][MANUAL_TEMPERATURE_KEY]))

        if is_temperature_within_margin(runtime_config[BOILER_STATUS_KEY][MANUAL_TEMPERATURE_KEY], runtime_config[TEMPERATURE_MARGIN_KEY], temperature, is_boiler_on):
            return True, '.5', ('Using default temperature %s. Temperature within margin. Boiler needs to be on' % (runtime_config[BOILER_STATUS_KEY][MANUAL_TEMPERATURE_KEY]))
        return False, '.4', ('Using default temperature %s. Temperature is too high. Boiler needs to be off' % (runtime_config[BOILER_STATUS_KEY][MANUAL_TEMPERATURE_KEY]))
    
    if is_system_in_schedule_mode() and not current_schedule:
        logging.debug('There is no schedule active at this moment. Temperature is irrelevant.')
        return False, '.8', 'Schedule mode but no active schedule. Boiler needs to be off'

    if is_system_in_schedule_mode() and current_schedule:
        if is_temperature_within_margin(current_schedule[TARGET_TEMPERATURE_JSON_KEY], runtime_config[TEMPERATURE_MARGIN_KEY], temperature, is_boiler_on):
            return True, '.2', 'Temperature within margin. Boiler needs to be on'
        return False, '.3', 'Temperature is too high. Boiler needs to be off'

    return False, '.9', 'How did we get to this. Boiler needs to be off'

def is_temperature_within_margin(target_temperature, margin, current_temperature, is_boiler_on):
    difference = target_temperature - current_temperature
    is_too_low = current_temperature < (target_temperature - margin)
    is_within_margin = abs(difference) < margin
    is_too_high = current_temperature >= (target_temperature + margin * 0.5)
    result = (is_too_low or (is_within_margin and is_boiler_on)) and not is_too_high
    logging.debug('current_temperature: %s | target_temperature: %s' % (current_temperature, target_temperature))
    logging.debug('temperature is too low: %s | temperature is within margin: %s (diff is %s) | is_too_high: %s | result: %s' % (is_too_low, is_within_margin, difference, is_too_high, result))
    return result

def calculate_new_boiler_state(is_boiler_on):
    if not runtime_config['is_system_on']:
        logging.debug('System is off')    
        return False, '5.0', 'System is off - System is off'
    # First calculate schedule state
    schedule_state, schedule_reason, schedule_reason_explanation = calculate_new_boiler_state_on_selected_mode()
    logging.debug('schedule_state: %s | schedule_reason: %s | schedule_reason_explanation: %s' % (schedule_state, schedule_reason, schedule_reason_explanation))
    # Now calculate temperature state
    temperature_state, temperature_reason, temperature_reason_explanation = calculate_new_boiler_state_on_temperature(is_boiler_on)
    logging.debug('temperature_state: %s | temperature_reason: %s | temperature_reason_explanation: %s' % (temperature_state, temperature_reason, temperature_reason_explanation))
    logging.debug('New state should be %s' % (schedule_state and temperature_state))
    return schedule_state and temperature_state, '%s%s' % (schedule_reason, temperature_reason), '%s - %s' % (schedule_reason_explanation, temperature_reason_explanation)

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def setup_relay_port():
    GPIO.setup(config.boiler['gpio_port'], GPIO.OUT)   
    GPIO.output(config.boiler['gpio_port'], GPIO.LOW)  

def action_boiler_relay(is_relay_on):
    #GPIO.setup(config.boiler['gpio_port'], GPIO.OUT)
    if is_relay_on:
        logging.debug("Turned on relay port")
        GPIO.output(config.boiler['gpio_port'], GPIO.HIGH)  
    else:
        logging.debug("Turned off relay port")
        GPIO.output(config.boiler['gpio_port'], GPIO.LOW)  

def heater_controller_actioner():
    state, reason, reason_explanation = calculate_new_boiler_state(runtime_config[BOILER_STATUS_KEY][IS_BOILER_ON_KEY])
    state_text = get_boiler_text_value_for(state)

    now = datetime.utcnow()

    commonFunctions.save_heater_data(state_text, reason, reason_explanation, now.isoformat(), now.isoformat())
    runtime_config[BOILER_STATUS_KEY][IS_BOILER_ON_KEY] = state
    logging.debug("is_boiler_on: %s | is_current_schedule_overriden: %s | last_scheduled_value: %s" % (runtime_config[BOILER_STATUS_KEY][IS_BOILER_ON_KEY], runtime_config[BOILER_STATUS_KEY][IS_CURRENT_SCHEDULE_OVERRIDEN_KEY], runtime_config[BOILER_STATUS_KEY][LAST_SCHEDULED_VALUE_KEY]))
    action_boiler_relay(state)

def heater_controller_daemon():
    logging.info("Starting Heater Controller Daemon")
    setup_relay_port()
    while(True):
        heater_controller_actioner()
        sleep(config.boiler['sleep_time_in_seconds_between_checks'])

def web_app_main():
    logging.info("Starting webapp")
    debug = logging.getLogger().isEnabledFor(logging.DEBUG)
    if not debug:
        log_flask = logging.getLogger('werkzeug')
        log_flask.setLevel(logging.ERROR)

    app.run(debug=debug, use_reloader=False, host=config.webapp['listening_ip'],ssl_context=config.webapp['sslConfig'])

def main():
    try:
        logging.info("Saving to file: %s" % (config.file['save_to_file']))
        logging.info("Saving to DB: %s" % (config.mysql['save_to_DB']))
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'
        t = threading.Thread(name='web_app_main',target=web_app_main)
        t.setDaemon(True)
        t.start()
        heater_controller_daemon()
    except KeyboardInterrupt:
        logging.error("bye!")
        sys.exit(1)
    except Exception as e:
        logging.error("Other error occurred")
        logging.error (e)
        logging.error(traceback.format_exc())
        sys.exit(1)
    finally:
        logging.debug("Cleaning GPIO port")
        GPIO.cleanup()
        logging.info("Shutting Down")

# call main
if __name__ == '__main__':    
    main()
