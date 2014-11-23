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
            map.x -= (screen_size_x() * (FACTOR-1)/2) * map.scale;
            map.y -= (screen_size_y() * (FACTOR-1)/2) * map.scale;
        };

        this.zoomOut = function () {
            map.x += (screen_size_x() * (FACTOR-1)/2) * map.scale;
            map.y += (screen_size_y() * (FACTOR-1)/2) * map.scale;
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

    function retrieve_data($http, map) {
        $http.get("/api/core/systems").success(function(data, status, headers, config){
            var systems = data.results;
            map.systems = {};
            map.planets = {};
            for(var i in systems) {
                prepare_system(systems[i], map);
            }

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
                //connect to sector updates
                //
                this.subscription = connection.create_subscription('sector', function(data) {
                });
                this.subscription.subscribe('main');

                scope.$state = $state;
            }
        }
    });
})();
