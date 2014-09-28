(function() {
    var app = angular.module('game');

    app.directive('coreControlPanel', function ($http, currentShip) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/control_panel.html',
            scope: {
                map: '=map',
                accountData: '=accountData'
            },
            link: function(scope, element) {
                scope.changeShip = function(ship) {
                    currentShip.change(ship.id);
                    scope.ship_menu_expanded = false;
                };

                $http.get("/api/core/own_ships").success(function(data, status, headers, config){
                    scope.ships = data.results;
                    currentShip.change(scope.ships[0].id);
                });

                scope.ship_menu_expanded = false;
                scope.currentShip = currentShip;
            }
        }
    });
})();