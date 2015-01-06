(function() {
    var module = angular.module('game');

    module.service('citadel', ['$http', '$rootScope', function($http, $rootScope) {
        var that = this;

        var subscription = connection.create_subscription('building', function (data) {
            that.updateData(data.building);
            $rootScope.$apply();
        });

        $http.get("/api/core/buildings/Citadel").success(function (data) {
            that.updateData(data);
            subscription.subscribe(that.id);
        });

        that.updateData = function(data) {
            console.log(that);
            $.each(data, function(key, value) {
                that[key] = value;
            });
            console.log(that);
        }
    }]);
})();