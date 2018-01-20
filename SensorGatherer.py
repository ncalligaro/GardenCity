import serial
import datetime
import time
import re

import sys
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import spidev

import Adafruit_DHT
#import urllib2

LOCAL_TEMPERATURE_HUMIDITY_SENSOR_PORT = 23;  #BCM format

GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)
radio = NRF24(GPIO, spidev.SpiDev())

SCRIPT_START_DATE = datetime.datetime.utcnow()
MEASUREMENTS_FOLDER = 'measurements'

def configure_radio():
    pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]

    radio.begin(0, 17)

    radio.setPayloadSize(32)
    radio.setChannel(0x76)
    radio.setDataRate(NRF24.BR_1MBPS)
    radio.setPALevel(NRF24.PA_MIN)

    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()

    radio.openWritingPipe(pipes[0])
    radio.openReadingPipe(1, pipes[1])
    radio.printDetails()
    # radio.startListening()

def get_local_sensor_data():
    RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, LOCAL_TEMPERATURE_HUMIDITY_SENSOR_PORT)
    if RH is not None and T is not None:
        return (str(RH), str(T))
    else:
        return None, None

def get_remote_sensor_data():
    message = list("GETREADINGS")
    while len(message) < 32:
        message.append(0)

    start = time.time()
    radio.write(message)
    radio.startListening()

    while not radio.available(0):
        time.sleep(1 / 100)
        if time.time() - start > 5: #Wait 5 seconds
            break

    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())

    string = ""
    for n in receivedMessage:
        # Decode into standard unicode set
        if (n >= 32 and n <= 126):
            string += chr(n)
    response = "{}".format(string)
    #T: 18.80 - H: 53.90O
    pattern = re.compile("T: (\d+.\d*) - H: (\d+.\d*)", re.IGNORECASE)
    result = pattern.search(response)
    if result is None:
        radio.stopListening()
        return None, None
    T = result.group(1)
    RH = result.group(2)
    radio.stopListening()
    return RH, T

def save_record(place, humidity, temperature, measureTime, creationTime):
    f = open('%s/temps_%s.txt' % (MEASUREMENTS_FOLDER, SCRIPT_START_DATE.strftime("%Y-%m-%d_%H%M")),'a')

    if humidity is not None and temperature is not None:
        f.write("INSERT INTO measurement (place,type,value,unit,measurement_date,created_at) VALUES ('%s','humidity',%s,'P','%s','%s');\n" % (place, humidity, measureTime, creationTime))
        f.write("INSERT INTO measurement (place,type,value,unit,measurement_date,created_at) VALUES ('%s','temperature',%s,'C','%s','%s');\n" % (place, temperature, measureTime, creationTime))
    else:
        f.write("INSERT INTO measurement (place,type,value,unit,measurement_date,created_at) VALUES ('%s','humidity',%s,'P','%s','%s');\n" % (place, 'null', measureTime, creationTime))
        f.write("INSERT INTO measurement (place,type,value,unit,measurement_date,created_at) VALUES ('%s','temperature',%s,'C','%s','%s');\n" % (place, 'null', measureTime, creationTime))
    
    f.close()

def main():
    try:
        configure_radio()
        while True:
            now = datetime.datetime.utcnow()

            DRH, DT = get_local_sensor_data()
            save_record('Dining', DRH, DT, now.isoformat(), now.isoformat())

            RRH, RT = get_remote_sensor_data()
            save_record('Room', RRH, RT, now.isoformat(), now.isoformat())

            time.sleep(60)
    except KeyboardInterrupt:
        print "\nbye!"
    except Exception as e:
        print "\nOther error occurred"
        print (e)
    finally:
        print "\nCleaning GPIO port\n"
        GPIO.cleanup()

# call main
if __name__ == '__main__':
   main()
