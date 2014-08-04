(function() {
    var app = angular.module('game');

    app.controller('ControlPanelController', ['$http', function($http) {
        var controlPanel = this;
        controlPanel.ships = [];
        $http.get("/api/core/own_ships").success(function(data, status, headers, config){
            controlPanel.ships = data.results;
            controlPanel.currentShip = controlPanel.ships[0];
        });
    }]);

    app.directive('coreControlPanel', function () {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/control_panel.html',
            scope: {
                map: '=map',
                controlPanel: '=controlPanel'
            }
        }
    });
})();