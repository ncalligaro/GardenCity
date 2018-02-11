(function () {
  'use strict';

  angular.module('HeaterApp', ['moment-picker'])

  .controller('HeaterController', ['$scope', '$log', '$http', 
    function($scope, $log, $http) {

      $scope.isBoilerOn = false;
      $scope.isScheduleOverriden = false;
      $scope.schedules = [];
      $scope.newSchedule = { 'fromTime':'09:00', 'toTime':'10:00', 'dayOfWeek':'2', 'targetTemperature': '19' };
      $scope.temperatureList = [];

      $scope.getSchedules = function() {
        $http.get('/heater/schedule')
          .success(function(response){
            $scope.schedules = response;
          })
      };

      $scope.fillTemperatureList = function() {
        for(var i=15.0;i<23;i=i+0.5){
          $scope.temperatureList.push(i.toString());
        }
      };
      
      $scope.deleteSchedule = function(schedule){
        $scope.updateFormWithData(schedule);
        $http.delete('/heater/schedule/' + schedule['object_id'])
          .success(function(response){
            $scope.getSchedules();
          })
      };

      $scope.addSchedule = function(){
        $http.post('/heater/schedule', $scope.newSchedule)
        .success(function(response){
          $scope.getSchedules();
        })
      };

      $scope.updateFormWithData = function(schedule){
        $scope.newSchedule['fromTime'] = schedule['fromTime'];
        $scope.newSchedule['toTime'] = schedule['toTime'];
        $scope.newSchedule['dayOfWeek'] = schedule['dayOfWeek'];
        $scope.newSchedule['targetTemperature'] = schedule['targetTemperature'];
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

      //Executing functions at startup
      $scope.fillTemperatureList();
      $scope.getSchedules();
      setInterval(function(){
        $scope.getBoilerStatus();
      }, 10000);
    }
  ]);

}());