(function() {
    var app = angular.module('game');

    //TODO this should be probably a service
    app.controller('AccountController', ['$http', function ($http) {
        var account = this;
        account.data = {};

        account.subscription_details = connection.create_subscription('account', function (data) {
            account.data = data.data;
        });

        $http.get("/api/account").success(function (data, status, headers, config) {
            account.data = data;
            account.subscription_details.subscribe(data.id);
        });
    }]);
})();