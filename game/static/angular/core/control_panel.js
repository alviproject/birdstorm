(function() {
    var app = angular.module('game');

    app.controller('ControlPanelController', ['$http', function($http) {
        var controlPanel = this;
        controlPanel.ships = [];
    }]);

    app.directive('coreControlPanel', function ($http) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/control_panel.html',
            scope: {
                map: '=map',
                controlPanel: '=controlPanel'
            },
            link: function(scope, element) {
                var subscription = connection.create_subscription('ownship', function (data) {
                    scope.controlPanel.currentShipDetails = data.ship;
                    scope.$apply();
                });

                scope.changeShip = function() {
                    $http.get("/api/core/own_ships/"+scope.controlPanel.currentShip.id).success(function(data, status, headers, config){
                        scope.controlPanel.currentShipDetails = data;
                    });

                    subscription.subscribe(scope.controlPanel.currentShip.id);
                };

                $http.get("/api/core/own_ships").success(function(data, status, headers, config){
                    scope.controlPanel.ships = data.results;
                    scope.controlPanel.currentShip = scope.controlPanel.ships[0];
                    scope.controlPanel.currentShipDetails = scope.controlPanel.currentShip;
                    scope.changeShip();
                });
            }
        }
    });
})();