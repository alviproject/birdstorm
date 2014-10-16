(function() {
    var module = angular.module('game.account', []);

    module.config(function($stateProvider) {
        $stateProvider
            .state('account', {
            })
            .state('account.signup', {
                url: "/account/signup",
                onEnter: ['$stateParams', '$state', '$modal', function($stateParams, $state, $modal) {
                    $modal.open({
                        templateUrl: "/static/angular/account/signup.html",
                        keyboard: false,
                        backdrop: false,
                        controller: ['$scope', '$cookies', '$http', '$state', function($scope, $cookies, $http, $state) {
                            //TODO
                            $scope.dismiss = function() {
                                $scope.$dismiss();
                            };

                            $scope.save = function() {
                            };

                            $scope.csrf_token = $cookies['csrftoken'];

                            $scope.login = function(username, password) {
                                $http.post('/api/account/login', {
                                    username: username,
                                    password: password
                                }).success(function() {
                                    //$state.go('map');
                                    window.location.replace("/");
                                }).error(function() {
                                    $scope.message = "Invalid username or password";
                                });
                            }
                        }]
                    }).result.then(function(result) {
                            if (result) {
                                return $state.transitionTo("map");
                            }
                        });
                }]
            });
    });

    module.service('account', ['$http', '$rootScope', function($http, $rootScope) {
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