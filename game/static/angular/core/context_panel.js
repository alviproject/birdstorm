(function() {
    var app = angular.module('game');

    app.controller('ContextPanelController', ['$scope', '$timeout', function($scope, $timeout) {
        var contextPanel = this;
        this.switch = function (choice, data, detailsPanel) { //TODO remove detailsPanel parameter
            contextPanel.choice = choice;
            //set basic data, extended data will be requested
            contextPanel.data = data;

            var injector = angular.element(document).injector();
            var $http = injector.get('$http');
            $http.get("/api/core/"+choice+"s/"+data.id+"/")
                .success(function (data, status, headers, config) {
                    //set extended data
                    contextPanel.data = data;
                });
        }
    }]);

    app.directive('coreContextPanel', function($http) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/context_panel.html',
            scope: {
                contextPanel: '=contextPanel',
                controlPanel: '=controlPanel',
                detailsPanel: '=detailsPanel',
                map: '=map'
            },
            link: function(scope, element) {
                scope.go_to_system = function (system_id) {
                    var ship_id = this.controlPanel.currentShip.id;
                    $http.post('/api/core/own_ships/'+ship_id+'/move/', {
                        system_id: system_id
                    });
                };
                scope.distance = function() {
                    var ship_system = scope.map.ships[scope.controlPanel.currentShipDetails.id].system();
                    var system = scope.contextPanel.data;
                    var x1 = ship_system.x;
                    var x2 = system.x;
                    var y1 = ship_system.y;
                    var y2 = system.y;
                    return Math.sqrt(Math.pow(x1-x2, 2)+Math.pow(y1-y2, 2));
                }
            }
        }
    });
})();