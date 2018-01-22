#!/bin/sh

#Setup:
#pip search mysql
pip install mysql-connector
#If the previous does not work use this instead:
sudo apt-get -y install python-mysql.connector
#pip install mysql-connector-python

git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python setup.py install
cd ..
rm -r Adafruit_Python_DHT

echo 'Install NR24 bla'