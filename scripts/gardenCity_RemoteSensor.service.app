[Unit]
Description=Garden City Remote Sensor Gatherer

[Service]
ExecStart=/home/pi/GardenCity/programStarter.sh RemoteArduinoSensorGatherer.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

