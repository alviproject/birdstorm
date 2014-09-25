(function() {
    var module = angular.module('game.details_panel', []);

    module.config(function($stateProvider) {
        $stateProvider
            .state('map.system', {
                url: "/system/:system_id",
                templateUrl: "/static/angular/core/details_panel/system.html",
                resolve: {
                    system: function($http, $stateParams){
                        return $http.get("/api/core/systems/"+$stateParams.system_id+"/").then(function(data) {
                            return data.data;
                        });
                    }
                },
                controller: function($stateParams, $scope, system) {
                    $scope.system = system;
                }
            })
            .state('map.system.planet', {
                url: "/planet/:planet_id",
                templateUrl: "/static/angular/core/details_panel/planet/index.html",
                resolve: {
                    planet: function($http, $stateParams){
                        return $http.get("/api/core/planets/"+$stateParams.planet_id+"/").then(function(data) {
                            return data.data;
                        });
                    }
                },
                controller: function($stateParams, $scope, $state, planet) {
                    $scope.planet = planet;
                    $scope.go = function(route){
                        $state.go(route);
                    };
                    $scope.active = function(route){
                        return $state.is(route);
                    };
                    $scope.$on("$stateChangeSuccess", function(event, toState, toParams, fromState, fromParams) {
                        console.log(event, toState, toParams, fromState, fromParams);
                        $scope.tabs.forEach(function(tab) {
                            tab.active = $scope.active(tab.route);
                        });
                    });
                    $scope.tabs = [
                        {heading: "Planet", route: "", active: false},
                        {heading: "Resources", route: ".resources", active: false}
                    ];
                }
            })
            .state('map.system.planet.resources', {
                url: "/resources",
                templateUrl: "/static/angular/core/details_panel/planet/resources.html",
                controller: function($stateParams, $scope, system) {
                }
            })
    });

    module.controller('DetailsPanelController', ['request_id', "$scope", '$state', function(request_id, $scope, $state) {
        var detailsPanel = this;

        //
        // connect to details channel
        //
        detailsPanel.subscription_details = connection.create_subscription('planetdetails', function (data) {
            detailsPanel.data = data.planet;
            $scope.$apply();
        });

        this.switch = function (choice, data) {
            //planet
            //TODO once port will have it's own directive it shall be moved
            detailsPanel.quantities = [];
            var i;
            for(i = 0; i < 100; i++) {
                detailsPanel.quantities.push(1);
            }
            detailsPanel.warehouse_quantities = [];
            for(i = 0; i < 100; i++) {
                detailsPanel.warehouse_quantities.push(1);
            }

            detailsPanel.subscription_details.subscribe(data.id+"_"+request_id());//TODO change request_id to planet_id

            var injector = angular.element(document).injector();
            var $http = injector.get('$http');
            $http.get("/api/core/"+choice+"s/"+data.id+"/")
                .success(function (data, status, headers, config) {
                    //set extended data
                    detailsPanel.data = data;
                });
        }
    }]);

    module.directive('coreDetailsPanel', function($http) {
        return {
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

                scope.buy = function (building_id, resource, index) {
                    var quantity = this.detailsPanel.quantities[index];
                    this.detailsPanel.quantities[index] = 0;
                    var ship_id = this.controlPanel.currentShip.id;
                    $http.post('/api/core/buildings/'+building_id+'/buy/', {
                        ship_id: ship_id,
                        resource: resource,
                        quantity: quantity
                    });
                };

                scope.sell = function (building_id, resource, index) {
                    var quantity = this.detailsPanel.quantities[index];
                    this.detailsPanel.quantities[index] = 0;
                    var ship_id = this.controlPanel.currentShip.id;
                    $http.post('/api/core/buildings/'+building_id+'/sell/', {
                        ship_id: ship_id,
                        resource: resource,
                        quantity: quantity
                    });
                };

                scope.order = function (building_id, order, quantity) {
                    var ship_id = this.controlPanel.currentShip.id;
                    $http.post('/api/core/buildings/'+building_id+'/order/', {
                        ship_id: ship_id,
                        order: order,
                        quantity: quantity
                    });
                };

                scope.warehouseResources = function(building) {
                    var result = {};
                    $.each(building.resources, function(key, value) {
                        result[key] = {warehouse: value, ship: 0};
                    });
                    $.each(scope.controlPanel.currentShipDetails.resources, function(key, value) {
                        if(result.hasOwnProperty(key)) {
                            result[key].ship = value;
                        }
                        else {
                            result[key] = {warehouse: 0, ship: value};
                        }
                    });
                    return result;
                };

                scope.store = function(building_id, resource, quantity, action) {
                    var ship_id = this.controlPanel.currentShip.id;
                    $http.post('/api/core/buildings/'+building_id+'/store/', {
                        ship_id: ship_id,
                        resource: resource,
                        quantity: quantity,
                        action: action
                    });
                };

                var currentShipChanged = function() {
                };

                scope.$watch('controlPanel.currentShipDetails', function(newVal, oldVal){
                    currentShipChanged();
                });

                scope.changeBuilding = function(building) {
                    if(building.type==="Workshop") {
                        currentShipChanged = function() {
                            scope.workshopLocked = true;
                            $http.post('/api/core/buildings/'+building.id+'/analyze/', {
                                ship_id: scope.controlPanel.currentShipDetails.id
                            }).success(function(data) {
                                building.processes = data;
                                scope.workshopLocked = false;
                            });
                        };
                        currentShipChanged();
                    }
                };
            }
        }
    });
})();