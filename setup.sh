#!/bin/sh

#Setup:
#pip search mysql
pip install mysql-connector-python
#If the previous does not work use this instead:
sudo apt-get -y install python-mysql.connector
#pip install mysql-connector-python

git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python setup.py install
cd ..
rm -r Adafruit_Python_DHT

pip install Flask
pip install pyping
pip install tinydb
#mkdir -p ~/.config/systemd/user/
#cp scripts/gardenCity.service ~/.config/systemd/user/
#chmod +x ~/.config/systemd/user/gardenCity.service
#cp scripts/gardenCity.service ~/.config/systemd/user/
#chmod +x ~/.config/systemd/user/gardenCity.service


mv scripts/gardenCity_WebSensor.service.app scripts/gardenCity_WebSensor.service
mv scripts/gardenCity_RemoteSensor.service.app scripts/gardenCity_RemoteSensor.service
mv scripts/gardenCity_LocalSensor.service.app scripts/gardenCity_LocalSensor.service
mv scripts/gardenCity_HeaterControl.service.app scripts/gardenCity_HeaterControl.service
sudo cp /home/pi/GardenCity/scripts/* /etc/systemd/system/ 

sudo systemctl daemon-reload
sudo systemctl enable gardenCity_WebSensor
sudo systemctl start gardenCity_WebSensor
sudo systemctl status gardenCity_WebSensor.service

sudo systemctl daemon-reload
sudo systemctl enable gardenCity_RemoteSensor
sudo systemctl start gardenCity_RemoteSensor
sudo systemctl status gardenCity_RemoteSensor.service

sudo systemctl daemon-reload
sudo systemctl enable gardenCity_LocalSensor
sudo systemctl start gardenCity_LocalSensor
sudo systemctl status gardenCity_LocalSensor.service

sudo systemctl daemon-reload
sudo systemctl enable gardenCity_HeaterControl
sudo systemctl start gardenCity_HeaterControl
sudo systemctl status gardenCity_HeaterControl.service

echo 'Install NR24 bla'