(function() {

    angular.module('ErrorHandler', [])
        .factory('$exceptionHandler', function () {
            return function errorCatcherHandler(x) {
                console.error(x.stack);
                Raven.captureException(x);
            };
        });

    var app = angular.module('game', [
        'ngCookies',
        'ui.bootstrap',
        'ui.router',
        'ncy-angular-breadcrumb',
        'game.details_panel',
        'game.account',
        'ErrorHandler'
    ]);

    app.factory('request_id', [function() {
        var id = guid();
        return function() {
            return id;
        };
    }]);

    //TODO move to core
    app.service('currentShip', ['$http', '$rootScope', function($http, $rootScope) {
        var ship = this;

        var subscription = connection.create_subscription('ownship', function (data) {
            ship.updateData(data.ship);
            $rootScope.$apply();
        });

        ship.id = undefined;
        ship.change = function(id) {
            $http.get("/api/core/own_ships/"+id).success(function(data){
                ship.updateData(data);
            });
            subscription.subscribe(id);
        };

        ship.updateData = function(data) {
            $.each(data, function(key, value) {
                ship[key] = value;
            });
            $rootScope.$broadcast('currentShip:updated');
        }
    }]);

    app.config(function($stateProvider, $urlRouterProvider){
        $urlRouterProvider.otherwise("/map");

        //TODO move to map?
        $stateProvider
            .state('map', {
                url: "/map",
                templateUrl: "/static/angular/core/details_panel/index.html",
                resolve: {
                    accountPromise: function(account) {
                        return account.promise;
                    }
                },
                controller: function($state, account) {
                    if(!account.is_authenticated) {
                        $state.go('account.signup');
                    }
                }
            })
    });

    app.run(function ($http, $cookies, $rootScope, request_id) {
        $http.defaults.headers.common['X-CSRFToken'] = $cookies['csrftoken'];
        $http.defaults.headers.common['X-RequestID'] = request_id();
    });

    app.directive("sref", function ($http, $document, $state) {
        return {
            restrict: 'A',
            link: function (scope, element) {
                console.log(element)
            }
        }
    });

    //setup Google Analytics
    app.run(['$rootScope', '$location', '$window', function($rootScope, $location, $window){
        $rootScope.$on('$stateChangeSuccess', function() {
            if($window.ga) {
                $window.ga('send', 'pageview', {page: $location.path()});
            }
        });
    }]);
})();
