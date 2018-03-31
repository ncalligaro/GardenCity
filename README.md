System On/Off Switch:
   When off, kills everything and overrides any schedule until Boiler is on again
   When on, it follows Schedule Mode or Manual Mode

   Scheduled Mode
      if override for X minutes is on
         turn off
      else
         if active schedule is on
            if temperature is low on schedule room, then it turns on
            if temperature is high on schedule room, then it turns off
         if no active schedule then it turns off
         if more than one active schedule then pick one?


   Manual Mode
      When mantainTemperature, it follows default temperature on selected room.
         if temperature is low, then it turns on
         if temperature is high, then it turns off
      When not mantainTemperature, it turns off


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