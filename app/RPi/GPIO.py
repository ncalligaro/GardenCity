from config import config

import logging

logging.basicConfig(level=config.get_logging_level(),
                    format=config.runtime_variables['log_format'],
                    datefmt=config.runtime_variables['log_date_format'])

BOARD = 'BOARD'
OUT = 'OUT'
IN = 'IN'
BCM = 'BCM'
LOW = 'LOW'
HIGH = 'HIGH'

def setmode(a):
   logging.debug("Set Mode %s" % a)

def setup(a, b):
   logging.debug("Setup %s %s" % (a, b))

def output(a, b):
   logging.debug("Output %s %s" % (a, b))

def cleanup():
   logging.debug("Cleanup")

def setwarnings(flag):
   logging.debug("Set Warnings %s" % flag)