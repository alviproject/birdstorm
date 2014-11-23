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
                        controller: function($scope, $http, $state, system) {
                            $scope.system = system;
                            $scope.$state = $state;
                        }
                    },
                    content: {
                        templateUrl: "/static/angular/core/details_panel/system.html",
                        controller: function($stateParams, $scope, $state, $http, system) {

                            //TODO duplicated with goto from map.js
                            $scope.goto = function(state, params) {
                                $state.go(state, params);
                            };

                            $scope.system = system;
                            $scope.$state = $state;
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
                controller: function($stateParams, $scope, $state, $http, request_id, planet, system) {
                    $scope.planet = planet;
                    $scope.tabs = [
                        {heading: "Planet", route: "."}
                    ];

                    //buildings tabs
                    $.each(planet.buildings, function(i, building){
                        $scope.tabs.push({heading: building.type, route: "."+building.type+"({building_id:"+building.id+"})"});
                    });

                    var subscription = connection.create_subscription('planet', function (data) {
                        $scope.planet = data.planet;
                    });

                    subscription.subscribe(planet.id+"_"+request_id());
                }
            })
            .state(buildingState({
                type: "Port",
                controller: function($stateParams, $scope, $http, planet, building) {
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
                        if(!check_planet(currentShip, planet, $scope)) {
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
                type: "Warehouse",
                controller: function($stateParams, $scope, $http, planet, account, currentShip, building) {
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
                        if(!check_planet(currentShip, planet, $scope)) {
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
    });
})();
