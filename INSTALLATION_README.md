Allows to manage 



#Setup:
sudo apt-get install python{,3}-pip 
#pip search mysql
pip install mysql-connector-python
#If the previous does not work use this instead:
sudo apt-get -y install python-mysql.connector
#pip install mysql-connector-python

If you want to use sensor type DS18B20
   sudo pip install w1thermsensor
   OR:
      sudo apt-get install python3-w1thermsensor
      sudo apt-get install python-w1thermsensor

   Edit /boot/config.txt and add "dtoverlay=w1-gpio" at the end

pip install --user --upgrade google-api-python-client
pip install --user --upgrade google-auth google-auth-oauthlib google-auth-httplib2

git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python setup.py install
cd ..
rm -r Adafruit_Python_DHT

pip install Flask
pip install pyping
pip install tinydb
sudo pip install pytz

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

crontab -e
and then add:
5 19 * * * /home/pi/GardenCity/dbReplicator.py

echo 'Install NR24 bla'


#Other tools for dev:
pip install autopep8
#autopep8 -i LocalSensorGatherer.py  (makes modifications to the file in site to make it pep8 compliant)
#First one restarts disks on syno, the second one actually works
5 19 * * * /home/pi/GardenCity/dbReplicator.py > /tmp/dbReplicator.log 2>/tmp/dbReplicator.log
9 19 * * * /home/pi/GardenCity/dbReplicator.py > /tmp/dbReplicator.log 2>/tmp/dbReplicator.log

If using mariadb, the replicator requires version 10.1 to work properly and if you do have 10.1 then add the following to my.cnf
[mysqld]
innodb-defragment=1
