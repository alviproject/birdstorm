(function() {
    var app = angular.module('game');

    app.controller('DetailsPanelController', [function() {
        var detailsPanel = this;
        this.switch = function (choice, data) {
            detailsPanel.choice = choice;
            //set basic data, extended data will be requested
            detailsPanel.data = data;
            detailsPanel.scan_messages = [];

            var injector = angular.element(document).injector();
            var $http = injector.get('$http');
            $http.get("/api/core/"+choice+"s/"+data.id+"/")
                .success(function (data, status, headers, config) {
                    //set extended data
                    detailsPanel.data = data;
                });
        }
    }]);

    app.directive('coreDetailsPanel', function($http, request_id) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/details_panel.html',
            scope: {
                detailsPanel: '=detailsPanel',
                controlPanel: '=controlPanel'
            },
            link: function(scope, element) {
                //
                // connect to details channel
                //
                //TODO this should be planetdetails.planet.user_id
                this.subscription = connection.create_subscription('planetdetails', function (data) {
                    if(data.message !== undefined) {
                        scope.detailsPanel.scan_messages.push(data.message);
                    }
                    if(data.results !== undefined) {
                        scope.detailsPanel.data.scan_results[data.level] = data.results;
                    }
                    scope.$apply();
                });
                this.subscription.subscribe(request_id());

                scope.scan = function (planet_id, level) {
                    var ship_id = this.controlPanel.currentShip.id;
                    $http.post('/api/core/own_ships/'+ship_id+'/scan/', {
                        planet_id: planet_id,
                        level: level
                    });
                };

                scope.extract = function (planet_id, level, resource_type) {
                    var ship_id = this.controlPanel.currentShip.id;
                    $http.post('/api/core/own_ships/'+ship_id+'/extract/', {
                        planet_id: planet_id,
                        level: level,
                        resource_type: resource_type
                    });
                }
            }
        }
    });
})();