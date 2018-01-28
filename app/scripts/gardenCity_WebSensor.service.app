[Unit]
Description=Garden City Web Sensor Gatherer

[Service]
ExecStart=/home/pi/GardenCity/programStarter.sh WebSensorGatherer.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

