(function () {
  'use strict';

  angular.module('HeaterApp', ['moment-picker'])

  .controller('HeaterController', ['$scope', '$log', '$http', 
    function($scope, $log, $http) {

      $scope.boilerStatus = false;
      $scope.scheduleOverriden = false;
      $scope.schedules = [];
      $scope.newSchedule = { 'fromTime':'09:00', 'toTime':'10:00', 'dayOfWeek':'2', 'targetTemperature': '19' };
      $scope.temperatureList = [];

      $scope.getSchedules = function() {
        $http.get('/heater/schedule')
          .success(function(response){
            $scope.schedules = response;
          })
      };
      $scope.getSchedules();

      $scope.fillTemperatureList = function() {
        for(var i=15.0;i<23;i=i+0.5){
          $scope.temperatureList.push(i.toString());
        }
      };
      $scope.fillTemperatureList();

      $scope.deleteSchedule = function(schedule){
        $scope.updateFormWithData(schedule);
        $http.delete('/heater/schedule/' + schedule['object_id'])
          .success(function(response){
            $scope.getSchedules();
          })
      };

      $scope.addSchedule = function(){
        console.log($scope.newSchedule);
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
        $scope.boilerStatus = !$scope.boilerStatus;
      };

      $scope.toggleScheduleOverriden = function() {
        $scope.scheduleOverriden = !$scope.scheduleOverriden;
      };
      
      $scope.getBoilerStatusLegend = function() {
        var boilerStatusLegend = "off";
        $scope.boilerStatus && (boilerStatusLegend = "on");
        return boilerStatusLegend;
      };

      $scope.getScheduleOverridenStatusLegend = function() {
        var scheduleOverridenLegend = "is not";
        $scope.scheduleOverriden && (scheduleOverridenLegend = "is");
        return scheduleOverridenLegend;
      };
    }
  ]);

}());