[Unit]
Description=Garden City Local Sensor Gatherer

[Service]
ExecStart=/home/pi/GardenCity/programStarter.sh LocalSensorGatherer.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

