(function() {
    var app = angular.module('game');

    app.controller('AccountController', ['$http', function ($http) {
        var account = this;
        account.data = {};
        $http.get("/api/account").success(function (data, status, headers, config) {
            account.data = data;
            console.log(data);
        });
    }]);
})();