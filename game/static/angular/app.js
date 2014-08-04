(function() {

    var app = angular.module('game', ['ngCookies']);

    app.factory('request_id', [function() {
        var id = guid();
        console.log("request ID: ", id);
        return function() {
            return id;
        };
    }]);

    app.run(function ($http, $cookies, request_id) {
        $http.defaults.headers.common['X-CSRFToken'] = $cookies['csrftoken'];
        $http.defaults.headers.common['X-RequestID'] = request_id();
    })
})();
