(function() {
    var app = angular.module('game');

    app.service('account', ['$http', '$rootScope', function($http, $rootScope) {
        var account = this;

        var subscription = connection.create_subscription('account', function (data) {
            account.updateData(data.data);
            $rootScope.$apply();
        });

        account.promise = $http.get("/api/account").success(function (data) {
            account.updateData(data);
            subscription.subscribe(account.id);
        });

        account.updateData = function(data) {
            $.each(data, function(key, value) {
                account[key] = value;
            });
        }
    }]);
})();