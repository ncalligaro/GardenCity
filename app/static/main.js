(function () {
  'use strict';

  angular.module('HeaterApp', [])

  .controller('HeaterController', ['$scope', '$log',
    function($scope, $log) {

      $scope.boilerStatus = false;
      $scope.boilerStatusLegend = "off";

      $scope.toggleBoiler = function() {
        $log.log($scope.boilerStatus);
        $log.log($scope.boilerStatusLegend);
        $scope.boilerStatus = !$scope.boilerStatus;
        $scope.boilerStatusLegend = "off";
        $scope.boilerStatus && ($scope.boilerStatusLegend = "on");

      };
    }
  ]);

}());