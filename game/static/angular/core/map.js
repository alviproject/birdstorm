(function() {
    var app = angular.module('game');

    var system_types = {
        "WhiteDraft": {color: "white", stroke: "grey", r: 5},
        "BrownDraft": {color: "brown", stroke: "white", r: 5},
        "BlueDraft": {color: "blue", stroke: "white", r: 5},
        "BlackDraft": {color: "black", stroke: "white", r: 5},
        "RedDraft": {color: "red", stroke: "white", r: 5},
        "Draft": {color: "yellow", stroke: "white", r: 10},
        "RedGiant": {color: "red", stroke: "white", r: 20},
        "BlueSuperGiant": {color: "blue", stroke: "white", r: 30},
        "HyperGiant": {color: "blue", stroke: "white", r: 40},
        "NeutronStar": {color: "#66FFFF", stroke: "white", r: 3},
        "BlackHole": {color: "black", stroke: "white", r: 10},
        "Nebula": {color: "grey", stroke: "white", r: 20},
        "Protostar": {color: "grey", stroke: "white", r: 20}
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

    //following two function rescale elements from cartesian coordinates (scale -1.0 to +1.0) to current size of the window
    //TODO support changing size of a browser window
    function rescale_x(c) {
        var CONTAINER_SIZE = $("body").find("div.container").width();
        var SCREEN_SIZE = $("svg").width();
        return (c * CONTAINER_SIZE/2) + SCREEN_SIZE/2;
    }

    function rescale_y(c) {
        var SCREEN_SIZE = $("svg").height();
        return (-c+1) * SCREEN_SIZE/2;
    }

    function prepare_system(system, map) {
        jQuery.extend(system, system_types[system.type]);
        system.display_x = rescale_x(system.x);
        system.display_y = rescale_y(system.y)
        map.systems[system.id] = system;
    }

    function prepare_ship(ship, map) {
        var system = map.systems[ship.system_id];
        ship.system = function() {
            return system;
        };
        ship.display_x = ship.system().display_x;
        ship.display_y = ship.system().display_y;

        map.ships[ship.id] = ship;
    }

    function retrieve_data($http, map) {
        $http.get("/api/core/systems").success(function(data, status, headers, config){
            var systems = data.results;
            map.systems = {};
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
            });
            $("#map-placeholder").css("height", $("svg").height());
        });
    }

    app.directive('coreMap', function ($http, $document) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/map.html',
            scope: {
                contextPanelSwitch: '=contextPanelSwitch',
                map: '=map',
                detailsPanel: '=detailsPanel'
            },
            link: function (scope, element) {
                var map = scope.map;
                retrieve_data($http, map);

                scope.dataSwitch = function(choice, data) {
                    scope.contextPanelSwitch(choice, data);
                    scope.detailsPanel.choice = '';
                };

                //
                //support for map moving (using drag & drop)
                //
                var startX = 0;
                var startY = 0;
                map.x = 0;
                map.y = 0;

                element.on('mousedown', function(event) {
                    event.preventDefault();
                    startX = event.pageX - map.x;
                    startY = event.pageY - map.y;
                    $document.on('mousemove', mousemove);
                    $document.on('mouseup', mouseup);
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
                    var time = data.time;
                    var target_system = map.systems[data.target_system];
                    var element = d3.select("#ship_"+data.ship);
                    element.transition()
                        .duration(time*1000)
                        .tween("position", function() {
                            console.log(ship.system);
                            var x = d3.interpolateRound(ship.display_x, target_system.display_x);
                            var y = d3.interpolateRound(ship.display_y, target_system.display_y + target_system.r);
                            return function(t) {
                                ship.display_x = x(t);
                                ship.display_y = y(t);
                                scope.$apply();
                            };
                        });
                });
                this.subscription.subscribe('main');
            }
        }
    });
})();
