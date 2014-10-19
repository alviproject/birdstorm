(function() {
    var app = angular.module('game');

    var system_radiuses = {
        "WhiteDwarf": 15,
        "BrownDwarf": 15,
        "BlueDwarf": 15,
        "BlackDwarf": 15,
        "RedDwarf": 15,
        "Dwarf": 30,
        "RedGiant": 40,
        "BlueSuperGiant": 45,
        "HyperGiant": 50,
        "NeutronStar": 6,
        "BlackHole": 20,
        "Nebula": 40,
        "Protostar": 40
    };

    var planet_radiuses = {
        "TerrestrialPlanet": 10,
        "GasGiant": 50,
        "WaterPlanet": 10,
        "IcePlanet": 8,
        "RedPlanet": 10
    };

    app.controller('MapController', [function() {
        var map = this;
        map.scale = 1;
        var FACTOR = 1.1;

        this.zoomIn = function () {
            map.scale = map.scale * FACTOR;
        };

        this.zoomOut = function () {
            map.scale = map.scale / FACTOR;
        };

        this.reset = function () {
            map.scale = 1;
            map.x = 0;
            map.y = 0;
        };
    }]);

    function screen_size_x() {
        return $("svg#map").width();
    }

    function screen_size_y() {
        return $("svg#map").height();
    }

    //following two function rescale elements from cartesian coordinates (scale -1.0 to +1.0) to current size of the window
    //TODO support changing size of a browser window
    function rescale_x(c) {
        return (c + 1) * screen_size_x()/2;
    }

    function rescale_y(c) {
        return (-c+1) * screen_size_y()/2;
    }

    function prepare_system(system, map) {
        system.r = system_radiuses[system.type];
        system.display_x = rescale_x(system.x);
        system.display_y = rescale_y(system.y);
        system.size = 0.12 * screen_size_y();
        map.systems[system.id] = system;

        $.each(system.planets, function(i, planet){
            planet.display_x = planet.x*screen_size_x();
            planet.display_y = planet.y*screen_size_y();
            planet.r = planet_radiuses[planet.type];
            planet.system = system;
            map.planets[planet.id] = planet;
        });
    }

    function prepare_ship(ship, map) {
        var planet = map.planets[ship.planet_id];
        ship.planet = function() {
            return planet;
        };
        ship.set_planet = function(new_planet) {
            planet = new_planet;
        };
        ship.display_x = ship.planet().display_x + ship.planet().system.display_x;
        ship.display_y = ship.planet().display_y + ship.planet().system.display_y;

        map.ships[ship.id] = ship;
    }

    function retrieve_data($http, map) {
        $http.get("/api/core/systems").success(function(data, status, headers, config){
            var systems = data.results;
            map.systems = {};
            map.planets = {};
            for(var i in systems) {
                prepare_system(systems[i], map);
            }

            //TODO possibly could be done asynchronously and utilize AngularJS two-way binding
            //that would require that ship coordinates (x, y) are dynamically calculated basing on ship.system
            //coordinates
            //it also requires a separate test case (systems are retrieved after ships)
            $http.get("/api/core/ships").success(function(data, status, headers, config){
                var ships = data.results;
                map.ships = {};
                for(var i in ships) {
                    prepare_ship(ships[i], map);
                }
                map.new_ship_subscription.subscribe('main');
            });

            $("#map-placeholder").css("height", $("svg#map").height());
        });
    }

    app.directive('coreMap', function ($http, $document, $state) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/map.html',
            scope: {
                map: '=map'
            },
            link: function (scope, element) {
                var map = scope.map;

                //
                //receive new ship updates
                //
                map.new_ship_subscription = connection.create_subscription('newship', function(data) {
                    prepare_ship(data.ship, map);
                });

                retrieve_data($http, map);

                //
                //support for map moving (using drag & drop)
                //
                var startX = 0;
                var startY = 0;
                map.x = 0;
                map.y = 0;

                element.on('mousedown', function(event) {
                    if(event.button === 0) {
                        event.preventDefault();
                        startX = event.pageX - map.x;
                        startY = event.pageY - map.y;
                        $document.on('mousemove', mousemove);
                        $document.on('mouseup', mouseup);
                    }
                });

                function mousemove(event) {
                    map.y = event.pageY - startY;
                    map.x = event.pageX - startX;
                    scope.$apply();
                }

                function mouseup() {
                    $document.off('mousemove', mousemove);
                    $document.off('mouseup', mouseup);
                }

                //
                //connect to sector updates and add handler to animate ship movements
                //
                this.subscription = connection.create_subscription('sector', function(data) {
                    var ship = map.ships[data.ship];
                    var time = data.time ? data.time : 1;
                    var target_planet = map.planets[data.target_planet];
                    ship.set_planet(target_planet);

                    var element = d3.select("#ship_"+data.ship);
                    element.transition()
                        .duration(time*1000)
                        .tween("position", function() {
                            var x = d3.interpolateRound(ship.display_x, target_planet.display_x + target_planet.system.display_x);
                            var y = d3.interpolateRound(ship.display_y, target_planet.display_y + target_planet.system.display_y);
                            return function(t) {
                                ship.display_x = x(t);
                                ship.display_y = y(t);
                                scope.$apply();
                            };
                        });
                });
                this.subscription.subscribe('main');

                scope.$state = $state;
            }
        }
    });
})();
