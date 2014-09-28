(function() {
    var module = angular.module('game.details_panel', []);

    function buildingState(params) {
        var templateFile = params.templateFile || params.type;
        return {
            name: 'map.system.planet.'+params.type,
            url: "/"+params.type+"/:building_id",
            templateUrl: "/static/angular/core/details_panel/planet/"+templateFile+".html",
            data: {
                ncyBreadcrumbLabel: '{{building.type}}'
            },
            resolve: {
                building: function($http, $stateParams){
                    return $http.get("/api/core/buildings/"+$stateParams.building_id+"/").then(function(data) {
                        return data.data;
                    });
                }
            },
            controller: params.controller
        }
    }

    function providerController($scope, $http, currentShip, building) {
        $scope.building = building;

        $scope.order = function (building_id, order, quantity) {
            var ship_id = currentShip.id;
            $http.post('/api/core/buildings/'+building_id+'/order/', {
                ship_id: ship_id,
                order: order,
                quantity: quantity
            });
        };
    }

    module.config(function($stateProvider) {
        $stateProvider
            .state('map.system', {
                url: "/system/:system_id",
                templateUrl: "/static/angular/core/details_panel/system.html",
                data: {
                    ncyBreadcrumbLabel: 'System {{system.id}}'
                },
                resolve: {
                    system: function($http, $stateParams){
                        return $http.get("/api/core/systems/"+$stateParams.system_id+"/").then(function(data) {
                            return data.data;
                        });
                    },
                    accountPromise: function(account) {
                        return account.promise
                    }
                },
                controller: function($stateParams, $scope, $state, system) {
                    $scope.system = system;
                    $scope.$state = $state;
                    $scope.distance = function() {
                        return 0;
                        var ship_system = scope.map.ships[scope.controlPanel.currentShipDetails.id].system();
                        var system = scope.contextPanel.data;
                        var x1 = ship_system.x;
                        var x2 = system.x;
                        var y1 = ship_system.y;
                        var y2 = system.y;
                        return Math.sqrt(Math.pow(x1-x2, 2)+Math.pow(y1-y2, 2));
                    }
                }
            })
            .state('map.system.planet', {
                url: "/planet/:planet_id",
                templateUrl: "/static/angular/core/details_panel/planet/index.html",
                data: {
                    ncyBreadcrumbLabel: '{{planet.type}} {{planet.id}}'
                },
                resolve: {
                    planet: function($http, $stateParams){
                        return $http.get("/api/core/planets/"+$stateParams.planet_id+"/").then(function(data) {
                            return data.data;
                        });
                    }
                },
                controller: function($stateParams, $scope, $state, planet) {
                    $scope.planet = planet;
                    $scope.tabs = [
                        {heading: "Planet", route: "."},
                        {heading: "Resources", route: ".resources"}
                    ];
                    //add tabs for buildings
                    $.each(planet.buildings, function(i, building){
                        $scope.tabs.push({heading: building.type, route: "."+building.type+"({building_id:"+building.id+"})"});
                    });
                }
            })
            .state('map.system.planet.resources', {
                url: "/resources",
                templateUrl: "/static/angular/core/details_panel/planet/resources.html",
                data: {
                    ncyBreadcrumbLabel: 'Resources'
                },
                controller: function($stateParams, $scope, $http, currentShip, system) {
                    $scope.scan = function (planet_id, level) {
                        var ship_id = currentShip.id;
                        $http.post('/api/core/own_ships/'+ship_id+'/scan/', {
                            planet_id: planet_id,
                            level: level
                        });
                    };

                    $scope.extract = function (planet_id, level, resource_type) {
                        var ship_id = currentShip.id;
                        $http.post('/api/core/own_ships/'+ship_id+'/extract/', {
                            planet_id: planet_id,
                            level: level,
                            resource_type: resource_type
                        });
                    };
                }
            })
            .state(buildingState({
                type: "Port",
                controller: function($stateParams, $scope, $http, currentShip, building) {
                    $scope.building = building;
                    $scope.quantities = {};
                    $.each(building.prices, function(type, price) {
                        $scope.quantities[type] = 1;
                    });
                    $scope.currentShipLoad = function(resource) {
                        if(currentShip.resources && currentShip.resources[resource]) {
                            return currentShip.resources[resource];
                        }
                        return 0;
                    };
                    $scope.sell = function (building_id, resource) {
                        var quantity = $scope.quantities[resource];
                        $scope.quantities[resource] = 0;
                        var ship_id = currentShip.id;
                        $http.post('/api/core/buildings/'+building_id+'/sell/', {
                            ship_id: ship_id,
                            resource: resource,
                            quantity: quantity
                        });
                    };
            }}))
            .state(buildingState({
                type: "Smelter",
                templateFile: "Plant",
                controller: providerController
            }))
            .state(buildingState({
                type: "Workshop",
                controller: providerController
            }))
            .state(buildingState({
                type: "Refinery",
                templateFile: "Plant",
                controller: providerController
            }))
            .state(buildingState({
                type: "Factory",
                templateFile: "Plant",
                controller: providerController
            }))
            .state(buildingState({
                type: "Warehouse",
                controller: function($stateParams, $scope, $http, account, currentShip, building) {
                    $scope.building = building;

                    $scope.warehouseResources = {};
                    function updateWarehouseResources() {
                        $.each(building.resources, function(key, value) {
                            $scope.warehouseResources[key] = {warehouse: value, ship: 0, quantity: 0};
                        });
                        if(currentShip.resources) {
                            $.each(currentShip.resources, function(key, value) {
                                if($scope.warehouseResources.hasOwnProperty(key)) {
                                    $scope.warehouseResources[key].ship = value;
                                }
                                else {
                                    $scope.warehouseResources[key] = {warehouse: 0, ship: value, quantity: 0};
                                }
                            });
                        }
                    }

                    $scope.$on('currentShip:updated', function() {
                        updateWarehouseResources();
                    });

                    $scope.store = function(resource, quantity, action) {
                        $http.post('/api/core/buildings/'+building.id+'/store/', {
                            ship_id: currentShip.id,
                            resource: resource,
                            quantity: quantity,
                            action: action
                        });
                    };

                    var subscription_building = connection.create_subscription('buildinguser', function (data) {
                        building = data.building;
                        updateWarehouseResources();
                    });

                    subscription_building.subscribe(building.id+"_"+account.id);
                    updateWarehouseResources();
            }}))
            .state(buildingState({
                type: "Shipyard",
                templateFile: "Plant",
                controller: providerController
            }))
            .state('map.ship', {
                url: "/ship/:ship_id",
                templateUrl: "/static/angular/core/details_panel/ship.html",
                data: {
                    ncyBreadcrumbLabel: 'Ship {{ship.type}} {{ship.id}}'
                },
                resolve: {
                    ship: function($http, $stateParams){
                        return $http.get("/api/core/ships/"+$stateParams.ship_id+"/").then(function(data) {
                            return data.data;
                        });
                    }
                },
                controller: function($stateParams, $scope, ship) {
                    $scope.ship = ship;
                }
            })
    });
})();