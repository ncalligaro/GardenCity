#!/usr/bin/python
from config import config

import commonFunctions

import os
import requests
from flask import Flask, render_template, request

# import sys
# import serial
import datetime
import time
# import re
# import traceback
# import httplib
# import urllib
import json

# import sys
# import RPi.GPIO as GPIO
# from lib_nrf24 import NRF24
# import spidev

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == "POST":
        # get url that the user has entered
        try:
            url = request.form['url']
            r = requests.get(url)
            print(r.text)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
    return render_template('index.html', errors=errors, results=results)

def main():
    error_print("Starting loop")
    try:
        error_print("WOHAA!")
    except KeyboardInterrupt:
        print("\nbye!")
    except Exception as e:
        print("\nOther error occurred")
        print (e)
        print(traceback.format_exc())
    finally:
        print("\nCleaning GPIO port\n")
        # GPIO.cleanup()

# call main
if __name__ == '__main__':
   # main()
   app.run()
