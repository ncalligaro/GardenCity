(function () {
  'use strict';

  angular.module('HeaterApp', ['moment-picker','ui.toggle'])

  .controller('HeaterController', ['$scope', '$log', '$http', 
    function($scope, $log, $http) {

      $scope.isSystemOn = false;
      $scope.isBoilerOn = false;
      $scope.systemMode = null;
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
          .success(function(response){
            $scope.availablePlaces = response.map(function(elem){
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
          return "alert-info";
        }
        if (temperature >= 10 && temperature < 18) {
          return "alert-danger";
        }
        if (temperature >= 18 && temperature < 19) {
          return "alert-warning";
        }
        if (temperature >= 19 && temperature < 20) {
          return "alert-success";
        }
        if (temperature >= 20 && temperature < 22) {
          return "alert-warning";
        }
        if (temperature >= 22) {
          return "alert-danger";
        }
        return "alert-danger";
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
          .success(function(response){
            $scope.currentTemperatures[place] = response;
            $scope.currentTemperatures[place].roundedTemperature = Math.trunc(response.temperature*100)/100;
          })
      };

      $scope.getSchedules = function() {
        $http.get('/schedule')
          .success(function(response){
            $scope.schedules = response;
            $scope.getActiveSchedule();
          })
      };
      
      $scope.deleteSchedule = function(schedule){
        $scope.updateFormWithData(schedule);
        $http.delete('/schedule/' + schedule['object_id'])
          .success(function(response){
            $scope.getSchedules();
          })
      };

      $scope.addSchedule = function(){
        $http.post('/schedule', $scope.newSchedule)
        .success(function(response){
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
        .success(function(response){
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
        .success(function(response){
          $scope.isSystemOn = response.isSystemOn;
          $scope.maintainTemperature = response.maintainTemperature;
          $scope.manualLocation = response.manualLocation;
          $scope.manualTemperature = response.manualTemperature;
          $scope.scheduleOverridenStarted = (response.scheduleOverridenStarted==null?null:new Date(response.scheduleOverridenStarted));
          $scope.scheduleOverridenTime = response.scheduleOverridenTime;
          $scope.isBoilerOn = response.isBoilerOn;
          $scope.isCurrentScheduleOverriden = response.isCurrentScheduleOverriden;
        })
      };

      $scope.setSystemStatus = function() {
        $http.post('/system/status', {'isSystemOn' : $scope.isSystemOn})
        .success(function(response){
          $scope.getBoilerStatus();
        })
      };

      $scope.getSystemStatus = function(){
        $http.get('/system/status')
        .success(function(response){
          $scope.isSystemOn = response.isSystemOn;
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
        .success(function(response){
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
        .success(function(response){
          $scope.getMode();
          $scope.getBoilerStatus();
        })
      };

      $scope.getMode = function(){
        $http.get('/system/mode')
          .success(function(response){
            $scope.systemMode = response['mode'];
          })
      };

      $scope.getActiveSchedule = function() {
        $http.get('/schedule/active')
          .success(function(response){
            $scope.activeSchedule = response;
            $scope.updatePercentageOfActiveSchedule();
          })
      };

      //Executing functions at startup
       $scope.$evalAsync(
          function( $scope ) {
              $scope.getSystemStatus();
              $scope.getSchedules();
              $scope.getBoilerStatus();
              $scope.fetchCurrentTemperatures();
              $scope.fetchPlaces();
              $scope.newSchedule.dayOfWeek = $scope.currentDayOfWeekInPython();
          }
      );
      setInterval(function(){
        $scope.getBoilerStatus();
        $scope.fetchCurrentTemperatures();
        $scope.getSchedules();
      }, 60000);
    }
  ]);

}());