(function () {
  'use strict';

  angular.module('HeaterApp', ['moment-picker'])

  .controller('HeaterController', ['$scope', '$log', '$http', 
    function($scope, $log, $http) {

      $scope.isBoilerOn = false;
      $scope.isScheduleOverriden = false;
      $scope.schedules = [];
      $scope.newSchedule = { 'fromTime':'17:00', 'toTime':'23:55', 'dayOfWeek': '0', 'targetTemperature': '20.5', 'place': 'Dining' };
      $scope.temperatureList = [];
      $scope.currentTemperatures = [];
      $scope.availablePlaces = ['Room','Dining','city_London','Kitchen'];
      $scope.activeSchedule = {};

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
          maxAge = 60;
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

      $scope.fillTemperatureList = function() {
        for(var i=15.0;i<23;i=i+0.5){
          $scope.temperatureList.push(i.toString());
        }
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

      $scope.toggleBoiler = function() {
        $scope.isBoilerOn = !$scope.isBoilerOn;
        $scope.updateBoilerStatus();
      };

      $scope.toggleisScheduleOverriden = function() {
        $scope.isScheduleOverriden = !$scope.isScheduleOverriden;
        $scope.updateBoilerStatus();
      };
      
      $scope.getBoilerStatus = function() {
          $http.get('/heater/status')
          .success(function(response){
            $scope.isBoilerOn = response.isBoilerOn;
            $scope.isScheduleOverriden = response.isScheduleOverriden;
          })
      };

      $scope.updateBoilerStatus = function() {
        var boilerStatus = {};
        boilerStatus.isBoilerOn = $scope.isBoilerOn;
        boilerStatus.isScheduleOverriden = $scope.isScheduleOverriden;

        $http.put('/heater/status', boilerStatus)
        .success(function(response){
          $scope.isBoilerOn = response.isBoilerOn;
          $scope.isScheduleOverriden = response.isScheduleOverriden;
        })
      };

      $scope.getIsBoilerOnLegend = function() {
        var isBoilerOnLegend = "off";
        $scope.isBoilerOn && (isBoilerOnLegend = "on");
        return isBoilerOnLegend;
      };

      $scope.getIsScheduleOverridenStatusLegend = function() {
        var isScheduleOverridenLegend = "is not";
        $scope.isScheduleOverriden && (isScheduleOverridenLegend = "is");
        return isScheduleOverridenLegend;
      };

      $scope.isSameSchedule = function(schedule1, schedule2) {
        if (schedule1 === undefined || schedule2 === undefined){
          return false;
        }
        return (schedule1.dayOfWeek == schedule2.dayOfWeek && schedule1.fromTime == schedule2.fromTime && schedule1.toTime == schedule2.toTime);
      };

      $scope.getActiveSchedule = function() {
        $http.get('/schedule/active')
          .success(function(response){
            $scope.activeSchedule = response;
          })
      };

      //Executing functions at startup
      $scope.fillTemperatureList();
      $scope.getSchedules();
      $scope.getBoilerStatus();
      $scope.fetchPlaces();
      $scope.newSchedule.dayOfWeek = $scope.currentDayOfWeekInPython();
      setInterval(function(){
        $scope.getBoilerStatus();
        $scope.fetchCurrentTemperatures();
        $scope.getSchedules();
      }, 60000);
    }
  ]);

}());