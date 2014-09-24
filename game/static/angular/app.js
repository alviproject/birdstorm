(function() {

    var app = angular.module('game', ['ngCookies', 'ui.bootstrap', 'ui.router', 'game.details_panel']);

    app.factory('request_id', [function() {
        var id = guid();
        console.log("request ID: ", id);
        return function() {
            return id;
        };
    }]);

    app.config(function($stateProvider, $urlRouterProvider){
        $urlRouterProvider.otherwise("/map");

        //TODO move to map?
        $stateProvider
            .state('map', {
                url: "/map",
                templateUrl: "/static/angular/core/details_panel/index.html"
            })
    });

    app.run(function ($http, $cookies, request_id) {
        $http.defaults.headers.common['X-CSRFToken'] = $cookies['csrftoken'];
        $http.defaults.headers.common['X-RequestID'] = request_id();
    })
})();
