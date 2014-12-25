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
                type: "Citadel",
                controller: function($stateParams, $scope, $http, planet, account, building) {
                    $scope.building = building;

                    var subscription_building = connection.create_subscription('buildinguser', function (data) {
                        building = data.building;
                        updateWarehouseResources();
                    });

                    subscription_building.subscribe(building.id+"_"+account.id);
            }}))
    });
})();
