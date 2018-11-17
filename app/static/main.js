(function () {
  'use strict';

  angular.module('HeaterApp', ['moment-picker','ui.toggle'])

  .controller('HeaterController', ['$scope', '$log', '$http', 
    function($scope, $log, $http) {

      $scope.isSystemOn = false;
      $scope.isBoilerOn = false;
      $scope.systemMode = null;
      $scope.user = {'picture':'static/images/refresh.png'};
      $scope.manualTemperature = 20.7;
      $scope.manualLocation = 'Dining';
      $scope.maintainTemperature = false;
      $scope.scheduleOverridenStarted = null;
      $scope.isCurrentScheduleOverriden = false;
      $scope.scheduleOverridenTime = 1;
      $scope.schedules = [];
      $scope.newSchedule = { 'fromTime':'17:00', 'toTime':'23:55', 'dayOfWeek': '0', 'targetTemperature': 20.7, 'targetPlace': 'Dining' };
      $scope.temperatureList = [];
      $scope.currentTemperatures = [];
      $scope.availablePlaces = ['Room','Dining','city_London','Kitchen'];
      $scope.activeSchedule = null;
      $scope.activeSchedulePercentage = 0;

      $scope.isManualModeEnabled = function(){
        return $scope.systemMode == 'manual';
      };

      $scope.isScheduleModeEnabled = function(){
        return $scope.systemMode == 'schedule';
      };

      $scope.currentDayOfWeekInPython = function(){
        var dayIndex = (new Date()).getDay();
        dayIndex = dayIndex -1;
        if (dayIndex == -1){
          dayIndex = 6;
        }
        return String(dayIndex);
      };

      $scope.fetchPlaces = function() {
        $http.get('/places/temperature')
          .then(function onSuccess(response){
            $scope.availablePlaces = response.data.map(function(elem){
              return elem[0];
            });
            $scope.fetchCurrentTemperatures();
          })
      };

      $scope.isAnScheduleActive = function() {
        return ($scope.activeSchedule != null && typeof $scope.activeSchedule.targetPlace !== 'undefined');
      };

      $scope.updatePercentageOfActiveSchedule = function(){
        if ( ! $scope.isAnScheduleActive()) {
         $scope.activeSchedulePercentage = 0;
         return;
        }
        var total = $scope.activeSchedule.toTimeDecimal - $scope.activeSchedule.fromTimeDecimal;
        var now = new Date();
        var current = now.getHours() * 100 + now.getMinutes();
        $scope.activeSchedulePercentage = Math.round(100*(current - $scope.activeSchedule.fromTimeDecimal) * 100 / total) / 100 ;
      };

      $scope.getAlertTypeForTemperatureRange = function(temperature) {
        if (temperature < 10) {
          return "alert-verycold";
        }
        if (temperature >= 10 && temperature < 18) {
          return "alert-cold";
        }
        if (temperature >= 18 && temperature < 19) {
          return "alert-mildcold";
        }
        if (temperature >= 19 && temperature < 21) {
          return "alert-mild";
        }
        if (temperature >= 21 && temperature < 23) {
          return "alert-mildwarm";
        }
        if (temperature >= 23 && temperature < 26) {
          return "alert-warm";
        }
        if (temperature >= 26) {
          return "alert-verywarm";
        }
        return "alert-unknown";
      };

      $scope.fetchCurrentTemperatures = function() {
        for (var i = 0; i < $scope.availablePlaces.length; i++){
          $scope.fetchAndStoreTemperature($scope.availablePlaces[i]);
        }
      };

      $scope.fetchAndStoreTemperature = function(place){
        var maxAge = 5;
        if (place == 'city_London'){
          maxAge = 90;
        }
        $http({url:'/temperature/' + place,
               method: 'GET',
               params: {'maxAge': maxAge}})
          .then(function onSuccess(response){
            $scope.currentTemperatures[place] = response.data;
            $scope.currentTemperatures[place].roundedTemperature = Math.trunc(response.data.temperature*100)/100;
          })
      };

      $scope.getSchedules = function() {
        $http.get('/schedule')
          .then(function onSuccess(response){
            $scope.schedules = response.data;
            $scope.getActiveSchedule();
          })
      };
      
      $scope.deleteSchedule = function(schedule){
        $scope.updateFormWithData(schedule);
        $http.delete('/schedule/' + schedule['object_id'])
          .then(function onSuccess(response){
            $scope.getSchedules();
          })
      };

      $scope.addSchedule = function(){
        $http.post('/schedule', $scope.newSchedule)
        .then(function onSuccess(response){
          $scope.getSchedules();
        })
      };

      $scope.updateFormWithData = function(schedule){
        $scope.newSchedule['fromTime'] = schedule['fromTime'];
        $scope.newSchedule['toTime'] = schedule['toTime'];
        $scope.newSchedule['dayOfWeek'] = String(schedule['dayOfWeek']);
        $scope.newSchedule['targetTemperature'] = String(schedule['targetTemperature']);
        $scope.newSchedule['targetPlace'] = schedule['targetPlace'];
      };

      $scope.getOverrideTimeEndDate = function(){
        if ($scope.isCurrentScheduleOverriden){
          if ($scope.scheduleOverridenStarted != null){
            var endDate = new Date();
            endDate.setTime($scope.scheduleOverridenStarted.getTime() + ($scope.scheduleOverridenTime *60*60*1000)); 
            return endDate;
          } 
          return "N/A";
        }
        return "N/A";
      };

      $scope.toggleOverrideSchedule = function() {
        if ($scope.isCurrentScheduleOverriden){
          $scope.scheduleOverridenStarted = new Date();  
        } else {
          $scope.scheduleOverridenStarted = null;
        }
        $scope.updateOverridenStartedDate();
        $scope.setBoilerStatus();
      };
      
      $scope.updateOverridenStartedDate = function() {
        var overridenDate = {};
        overridenDate.scheduleOverridenStarted = ($scope.scheduleOverridenStarted==null?null:$scope.scheduleOverridenStarted.getTime());

        $http.put('/heater/overridenDate', overridenDate)
        .then(function onSuccess(response){
          $scope.getBoilerStatus();
        })
      };

      $scope.toggleMantainTemperature = function() {
        $scope.setBoilerStatus();
      };

      $scope.toggleSystem = function() {
        $scope.setBoilerStatus();
      };

      $scope.toggleBoiler = function() {
        $scope.setBoilerStatus();
      };
      
      $scope.getBoilerStatus = function() {
        $scope.getMode();
        $http.get('/heater/status')
        .then(function onSuccess(response){
          $scope.isSystemOn = response.data.isSystemOn;
          $scope.maintainTemperature = response.data.maintainTemperature;
          $scope.manualLocation = response.data.manualLocation;
          $scope.manualTemperature = response.data.manualTemperature;
          $scope.scheduleOverridenStarted = (response.data.scheduleOverridenStarted==null?null:new Date(response.data.scheduleOverridenStarted));
          $scope.scheduleOverridenTime = response.data.scheduleOverridenTime;
          $scope.isBoilerOn = response.data.isBoilerOn;
          $scope.isCurrentScheduleOverriden = response.data.isCurrentScheduleOverriden;
        })
      };

      $scope.setSystemStatus = function() {
        $http.post('/system/status', {'isSystemOn' : $scope.isSystemOn})
        .then(function onSuccess(response){
          $scope.getBoilerStatus();
        })
      };

      $scope.getSystemStatus = function(){
        $http.get('/system/status')
        .then(function onSuccess(response){
          $scope.isSystemOn = response.data.isSystemOn;
        })
      };

      $scope.updateSystemValues = function(){
        $scope.setBoilerStatus();
      }

      $scope.setBoilerStatus = function() {
        var boilerStatus = {};
        boilerStatus.isSystemOn = $scope.isSystemOn;
        boilerStatus.maintainTemperature = $scope.maintainTemperature;
        boilerStatus.manualLocation = $scope.manualLocation;
        boilerStatus.manualTemperature = $scope.manualTemperature;
        //boilerStatus.scheduleOverridenStarted = ($scope.scheduleOverridenStarted==null?null:$scope.scheduleOverridenStarted.getTime());
        boilerStatus.scheduleOverridenTime = $scope.scheduleOverridenTime;
        boilerStatus.isCurrentScheduleOverriden = $scope.isCurrentScheduleOverriden;

        $http.put('/heater/status', boilerStatus)
        .then(function onSuccess(response){
          $scope.getBoilerStatus();
        })
      };

      $scope.isPlaceDrivingTemperature = function(place){
        if ($scope.isManualModeEnabled()){
          return $scope.manualLocation == place;
        }
        if ($scope.isScheduleModeEnabled()){
          if ($scope.activeSchedule == null || typeof $scope.activeSchedule.targetPlace === 'undefined') {
            return false;
          }
          if ($scope.activeSchedule.targetPlace == place){
            return true;
          }  
        }
        
        return false;
      };

      $scope.getIsBoilerOnLegend = function() {
        var isBoilerOnLegend = "off";
        $scope.isBoilerOn && (isBoilerOnLegend = "on");
        return isBoilerOnLegend;
      };

      $scope.getIsCurrentScheduleOverridenLegend = function() {
        var isCurrentScheduleOverridenLegendLegend = "not overriden";
        $scope.isCurrentScheduleOverriden && (isCurrentScheduleOverridenLegendLegend = "overriden");
        return isCurrentScheduleOverridenLegendLegend;
      };

      $scope.isSameSchedule = function(schedule1, schedule2) {
        if (typeof schedule1 === undefined || typeof schedule2 === undefined){
          return false;
        }
        if (schedule1 == null || schedule2 == null){
          return false;
        }
        return (schedule1.dayOfWeek == schedule2.dayOfWeek && schedule1.fromTime == schedule2.fromTime && schedule1.toTime == schedule2.toTime);
      };

      $scope.setMode = function(mode){
        $scope.systemMode = mode;
        console.log(mode);
        if ($scope.isScheduleModeEnabled()){
          console.log("wtf");
          $scope.isCurrentScheduleOverriden = false;
        }
        $http.post('/system/mode', {'mode' : $scope.systemMode})
        .then(function onSuccess(response){
          $scope.getMode();
          $scope.getBoilerStatus();
        })
      };

      $scope.getMode = function(){
        $http.get('/system/mode')
          .then(function onSuccess(response){
            $scope.systemMode = response.data['mode'];
          })
      };

      $scope.getActiveSchedule = function() {
        $http.get('/schedule/active')
          .then(function onSuccess(response){
            $scope.activeSchedule = response.data;
            $scope.updatePercentageOfActiveSchedule();
          })
      };

      $scope.fetchUsername = function() {
        $http.get('/user')
          .then(function onSuccess(response){
            $scope.user = response.data;
          })
      };

      //Executing functions at startup
       //$scope.$evalAsync(
       //   function( $scope ) {
              $scope.fetchUsername();
              $scope.getSystemStatus();
              $scope.getSchedules();
              $scope.getBoilerStatus();
              $scope.fetchCurrentTemperatures();
              $scope.newSchedule.dayOfWeek = $scope.currentDayOfWeekInPython();
              $scope.fetchPlaces();
        //  }
      //);
      setInterval(function(){
        $scope.getBoilerStatus();
        $scope.fetchCurrentTemperatures();
        $scope.getSchedules();
      }, 60000);
    }
  ]);

}());