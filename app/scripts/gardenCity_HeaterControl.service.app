[Unit]
Description=Garden City Heater Control

[Service]
ExecStart=/home/pi/GardenCity/programStarter.sh HeaterControl.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

