(function() {
    var app = angular.module('game');

    app.controller('DetailsPanelController', ['request_id', function(request_id) {
        var detailsPanel = this;
        //
        // connect to details channel
        //
        detailsPanel.subscription_actions = connection.create_subscription('planetactionsprogress', function (data) {
            detailsPanel.scan_messages.push(data.message);
        });
        detailsPanel.subscription_details = connection.create_subscription('planetdetails', function (data) {
            detailsPanel.data = data.planet;
        });

        this.switch = function (choice, data) {
            detailsPanel.choice = choice;
            //set basic data, extended data will be requested
            detailsPanel.data = data;
            detailsPanel.scan_messages = [];
            detailsPanel.subscription_actions.subscribe(data.id+"_"+request_id());//TODO change request_id to planet_id

            var injector = angular.element(document).injector();
            var $http = injector.get('$http');
            $http.get("/api/core/"+choice+"s/"+data.id+"/")
                .success(function (data, status, headers, config) {
                    //set extended data
                    console.log(data);
                    detailsPanel.data = data;
                });
        }
    }]);

    app.directive('coreDetailsPanel', function($http) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/details_panel.html',
            scope: {
                detailsPanel: '=detailsPanel',
                controlPanel: '=controlPanel'
            },
            link: function(scope, element) {
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
                };

                scope.buy = function (building_id, resource, price) {
                    var quantity = price.quantity;
                    price.quantity = 0;
                    var ship_id = this.controlPanel.currentShip.id;
                    $http.post('/api/core/buildings/'+building_id+'/buy/', {
                        ship_id: ship_id,
                        resource: resource,
                        quantity: quantity
                    });
                }
            }
        }
    });
})();