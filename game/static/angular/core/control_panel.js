(function() {
    var app = angular.module('game');

    app.directive('coreControlPanel', function ($http, currentShip, account) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/control_panel.html',
            scope: {
                map: '=map'
            },
            controller: function($scope) {
                $scope.changeShip = function(ship) {
                    currentShip.change(ship.id);
                    $scope.ship_menu_expanded = false;
                };

                $scope.ship_menu_expanded = false;
                $scope.currentShip = currentShip;
                $scope.account = account;

                var subscription = connection.create_subscription('ownships', function (data) {
                    $scope.ships = data.ships;
                    if(data.current_ship_id != currentShip.id) {
                        currentShip.change(data.current_ship_id);
                    }
                });

                $scope.$watch('account.id', function() {
                    if(!account.id) {
                        return;
                    }
                    $http.get("/api/core/own_ships").success(function(data){
                        $scope.ships = data.results;
                        currentShip.change($scope.ships[0].id);
                    });

                    subscription.subscribe(account.id);
                });
            }
        }
    });
})();