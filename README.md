This project allows you to take control of your boiler by stating which zone it should keep track of at diferent times in the day.
It's not fully multi-zone yet, as it needs electronic radiator valves and a little more development for that.

System On/Off Switch:
   When off, kills everything and overrides any schedule until Boiler is on again
   When on, it follows Schedule Mode or Manual Mode

   Scheduled Mode
      if snooze is off then
         if active schedule is on
            if temperature is low on schedule room, then it turns on (within setting temperature_margin)
            if temperature is high on schedule room, then it turns off (within setting temperature_margin)
         if no active schedule then it turns off
         if more than one active schedule then it picks higher temperature
      else
         if maintain temperature is No
            it turns off the boiler for "Snooze for" time
         else
            it follows same principles as scheduled but on Room Driving temperature, using Target Temperature, for the amount of time "Snooze for" and then reverts back to schedule mode


   Manual Mode
      When mantainTemperature, it follows Target Temperature on selected room.
         if temperature is low, then it turns on
         if temperature is high, then it turns off
      When not mantainTemperature, it turns off

There is also a DB Replicator script that allows you to run it on a very low storage system, and then sync daily data to another storage database for history purposes. If you don't need this then don't deploy the #Temporary Satellite database

Settings:
runtimeSettings.json: Defines runtime variables, like default temperatures and currently selected mode (to restore from in case of power failure)
* is_system_on: whether the system is on or off ("System is" value)
* system_mode: Which system mode is selected, Manual or Schedule ("System Mode" value)
* available_places: List of temperature zones. This list is populated automatically from DB values
* boiler_status:
   * schedule_overriden_started: Time when the schedule override started (For tracking when it should end)
   * manual_location: Which temperature zone is selected for schedule override or manual mode ("Room Driving temperature" value)
   * is_boiler_on: calculated value of current boiler status ("Boiler is" value)
   * maintain_temperature: Defines if temperature should be kept stable in schedule overriden or manual modes ("Maintain Temperature?" value)
   * manual_temperature: Defines the target temperature for schedule overriden or manual modes ("Target Temperature" value)
   * schedule_overriden_time: Defines for how long the schedule should be overriden since schedule_overriden_started ("Snooze For" value)
* temperature_margin: defines a delta around manual_temperature (or the schedule temperature) during which the current boiler status should be kept the same. This is for control stabilization purposes.
* allowed_logins: List of google email addresses allowed to log in to the service

config.py: defines configuration values, mostly related to sensors and database connection.
* mysql: stores configuration regarding DB connection. "save_to_DB" enables or disables storing to DB
* file: stores configuration for storing sensor information when file mode is on. "save_to_file" enables or disables storing to file
* open_map: used to get temperatures for city. Needs an openwhethermap account.
* local_sensors: contains local sensors to read temperatures and humidity from. Accepts sensors models DHT11, DHT22 and DS18B20 (last one is temperature only but it's useful for getting feedback from boiler pipes' temperature)
* remote_arduino_sensor: it was inteded to be used in junction with remote arduino sensors connected to a raspberry pi via NRF24L01+ devices. Unfortunately these are very unstable and troubleshooting them takes too much time. It's a lot easier to buy an old raspberry pi and add a wifi usb card)
* runtime_variables: containes a number of configs related to logs mostly and timestamps
* boiler: defines which port contains the relay to control the boiler and how often should the state of the boiler be calculated
* webapp: defines on which IP should the web interface listen and which certificates to use. If you don't want to use SSL then open HeaterControl.py and look for line:
   app.run(debug=debug, use_reloader=False, host=config.webapp['listening_ip'], ssl_context=config.webapp['sslConfig'])
replace it with:
   app.run(debug=debug, use_reloader=False, host=config.webapp['listening_ip'])

client_secret.json: contains Google configuration values to enable Authentication. I did not code a way to bypass this so you might need to do that yourself if you don't want/need authentication. However, be adviced not having authentication is a really bad idea in modern times.

schedulesDB.json: stores the schedules configuration. 





Log Reason Code Base
Format: x.y
X is the schedule/manual reason
Y is the temperature reason

X codes:
0: Unknown reason
1: Schedule overriden. Returning maintainTemperature
2: Schedule temporarily overriden but scheduled value changed. Returned new value
3: Schedule temporarily overriden but scheduled value has not changed. Returned previous value
4: Following schedule. Returned schedule value X
5: System is off
6: Manual mode, returning mantainTemperature value

Y codes:
.0 System is off
.1
.2 Temperature within margin. Boiler needs to be on
.3 Temperature is too high. Boiler needs to be off
.4 Using default temperature %s. Temperature is too high. Boiler needs to be off
.5 Using default temperature %s. Temperature within margin. Boiler needs to be on
.6 Unable to read %s temperature
.7 Unable to read avg %s temperature
.8 Schedule mode but no active schedule. Boiler needs to be off
.9 How did we get to this. Boiler needs to be off -- Error mode

Make sure I2C and SPI are disabled in raspi-config or depending of the outputs used it may cause issues