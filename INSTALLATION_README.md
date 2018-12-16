The project is composed of several components that run independently.  
These are started by the scripts included in the "app/scripts" folder.  
There is no need to run them all and no need to run them all on the same device.  
  
  
The required ones are:  
- HeaterControl: Starts the web interface and the boiler controlling system. This needs to run in a device connected to the boiler in order to start/stop it. Most boilers have a set of 12-24v pins that turn on and off the boiler  
- at least one LocalSensor  
  
Optional:  
- WebSensor: If you want to include city temperature statistics  
- DBReplicator: if you have little storage on your device, but also have a big NAS somewhere running a MySQL db and wish to retain historic data  
  
For installation the first step is to copy the whole repository to all devices where at least one component needs to be run, except app/RPi, which is only used for development on non-raspberrypi machines.  
Then we need to install the pre-requisites.  
Remember to install Python libraries as the user configured to run the services.  
  
```
sudo cp <wherever_garden_city_root_folder_is>/scripts/* /etc/systemd/system/ 
sudo systemctl daemon-reload

sudo apt-get install python{,3}-pip 
pip install --user mysql-connector-python
#If the previous does not work use this instead:
sudo apt-get -y install python-mysql.connector
pip install --user spidev
pip install --user --upgrade google-api-python-client
pip install --user --upgrade google-auth google-auth-oauthlib google-auth-httplib2
```
If you want to use sensor type DHT11 or DHT22, you'll need to install the module via PIP:  
```pip install --user Adafruit_DHT ```
OR by building the component yourself:  
```
cd <wherever_garden_city_root_folder_is>
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python setup.py install
cd ..
rm -r Adafruit_Python_DHT
```
  
If you want to use sensor type DS18B20, you can install it via PIP:  
```sudo pip install w1thermsensor ```
or via apt-get:  
```
sudo apt-get install python3-w1thermsensor
sudo apt-get install python-w1thermsensor
```
you will also need to edit ```/boot/config.txt``` and add ```dtoverlay=w1-gpio``` at the end  

Make sure I2C and SPI are disabled in raspi-config or depending of the outputs used it may cause issues  
```
raspi-config -> interfacing options
Disable I2C
Enable SPI
```

To enable the web sensor service, start it, and then check the status:  
```
sudo systemctl enable gardenCity_WebSensor
sudo systemctl start gardenCity_WebSensor
sudo systemctl status gardenCity_WebSensor

same for RemoteSensor, LocalSensor, HeaterControl
sudo systemctl enable gardenCity_RemoteSensor
sudo systemctl start gardenCity_RemoteSensor
sudo systemctl status gardenCity_RemoteSensor

sudo systemctl enable gardenCity_LocalSensor
sudo systemctl start gardenCity_LocalSensor
sudo systemctl status gardenCity_LocalSensor

sudo systemctl enable gardenCity_HeaterControl
sudo systemctl start gardenCity_HeaterControl
sudo systemctl status gardenCity_HeaterControl
```
Additional Instructions  
for HeaterControl component:  
```
pip install Flask
pip install pyping
pip install tinydb
sudo pip install pytz
```  
for DBReplicator:  
```crontab -e```  
and then add:  
```5 19 * * * /home/pi/GardenCity/dbReplicator.py```  
If using mariadb, the replicator requires version 10.1 to work properly and if you do have 10.1 then add the following to my.cnf  
[mysqld]  
```innodb-defragment=1```
  
  
If you want to use NRF24.py, then make sure lib_nrf24.py is in the same folder as the rest of the py files
  
  
  
If you want ot continue developing, you might find some of the following instructions useful. If you only want to use the system as is then skip the following:
#Other tools for dev:  
```pip install autopep8```  
#autopep8 -i LocalSensorGatherer.py  (makes modifications to the file in site to make it pep8 compliant)  
#First one restarts disks on syno, the second one actually works  
```
5 19 * * * /home/pi/GardenCity/dbReplicator.py > /tmp/dbReplicator.log 2>/tmp/dbReplicator.log  
9 19 * * * /home/pi/GardenCity/dbReplicator.py > /tmp/dbReplicator.log 2>/tmp/dbReplicator.log  
```
