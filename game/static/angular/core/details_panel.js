(function() {
    var module = angular.module('game.details_panel', []);
    var show_wrong_system_alert = false;

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

    function providerController($scope, $http, system, currentShip, building) {
        $scope.building = building;
        $scope.currentShip = currentShip;

        $scope.quantities = {};
        $.each(building.processes, function(resource, details) {
            if(!currentShip.resources) {
                //currentShips may not be ready yet
                // this happens when this state is evaluated before currentShip is retrieved
                $scope.quantities[resource] = 1;
            }
            else {
                $scope.quantities[resource] = 100;
                $.each(details.requirements, function(requirement, quantity) {
                    var max = Math.floor((currentShip.resources[requirement] || 0) / quantity);
                    $scope.quantities[resource] = Math.min($scope.quantities[resource], max);
                });
            }
        });

        $scope.order = function (building_id, order, quantity) {
            var ship_id = currentShip.id;
            if(!check_system(currentShip, system, $scope)) {
                return
            }
            $scope.quantities[order] = 1;
            $http.post('/api/core/buildings/'+building_id+'/order/', {
                ship_id: ship_id,
                order: order,
                quantity: quantity
            });
        };
    }

    function workshopController($scope, $http, currentShip, building) {
        providerController($scope, $http, currentShip, building);
        $scope.$watch('currentShip.components', function() {
           if(currentShip.id) {
               $http.post('/api/core/buildings/'+building.id+'/analyze/', {
                   ship_id: currentShip.id
               }).success(function(data) {
                   building.processes = data;
               });
           }
        });
    }

    function create_go_to_system($http, currentShip) {
        return function(system_id) {
            $http.post('/api/core/own_ships/'+currentShip.id+'/move/', {
                system_id: system_id
            });
            wrong_system_alert(false);
        }
    }

    function check_system(currentShip, system) {
        if(currentShip.system_id !== system.id) {
            wrong_system_alert(true);
            return false;
        }
        return true;
    }

    function wrong_system_alert(show) {
        if(show === undefined) {
            return show_wrong_system_alert;
        }
        show_wrong_system_alert = show;
    }

    module.config(function($stateProvider) {
        $stateProvider
            .state('map.system', {
                url: "/system/:system_id",
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
                views: {
                    action: {
                        templateUrl: "/static/angular/core/details_panel/system_action.html",
                        controller: function($scope, $http, $state, currentShip, system) {
                            $scope.currentShip = currentShip;
                            $scope.system = system;
                            $scope.go_to_system = create_go_to_system($http, currentShip);
                        }
                    },
                    content: {
                        templateUrl: "/static/angular/core/details_panel/system.html",
                        controller: function($stateParams, $scope, $state, $http, system, currentShip) {

                            //TODO duplicated with goto from map.js
                            $scope.goto = function(state, params) {
                                $state.go(state, params);
                            };

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
                            };
                            $scope.go_to_system = create_go_to_system($http, currentShip);
                            $scope.wrong_system_alert = wrong_system_alert;
                        }
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
                controller: function($stateParams, $scope, $state, request_id, planet) {
                    $scope.planet = planet;
                    $scope.tabs = [
                        {heading: "Planet", route: "."},
                    ];

                    //resources tab
                    if(planet.buildings.length === 0) {
                        $scope.tabs.push({heading: "Resources", route: ".resources"});
                    }

                    //buildings tabs
                    $.each(planet.buildings, function(i, building){
                        $scope.tabs.push({heading: building.type, route: "."+building.type+"({building_id:"+building.id+"})"});
                    });

                    var subscription = connection.create_subscription('planetdetails', function (data) {
                        $scope.planet = data.planet;
                    });

                    subscription.subscribe(planet.id+"_"+request_id());
                }
            })
            .state('map.system.planet.resources', {
                url: "/resources",
                templateUrl: "/static/angular/core/details_panel/planet/resources.html",
                data: {
                    ncyBreadcrumbLabel: 'Resources'
                },
                controller: function($stateParams, $scope, $http, currentShip, system) {
                    $scope.currentShip = currentShip;
                    $scope.wrong_system_alert = wrong_system_alert;
                    $scope.scan = function (planet_id) {
                        if(!check_system(currentShip, system, $scope)) {
                            return
                        }
                        var ship_id = currentShip.id;
                        $http.post('/api/core/own_ships/'+ship_id+'/scan/', {
                            planet_id: planet_id
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
                controller: function($stateParams, $scope, $http, system, currentShip, building) {
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
                        if(!check_system(currentShip, system, $scope)) {
                            return
                        }
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
                controller: workshopController
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
                controller: function($stateParams, $scope, $http, system, account, currentShip, building) {
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
                        if(!check_system(currentShip, system, $scope)) {
                            return
                        }
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
                templateFile: "Shipyard",
                controller: providerController
            }))
            .state('map.ship', {
                url: "/ship/:ship_id",
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
                views: {
                    content: {
                        templateUrl: "/static/angular/core/details_panel/ship.html",
                        controller: function($stateParams, $scope, ship) {
                            $scope.ship = ship;
                        }
                    }
                }
            })
    });
})();