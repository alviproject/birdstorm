(function() {
    var app = angular.module('game');

    app.directive('coreOverviewPanel', function ($http, citadel, account) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/overview_panel.html',
            scope: {
            },
            controller: function($scope) {
                $scope.changeView = function(view) {
                    $scope.menu_expanded = false;
                    $scope.currentView = view;
                };

                $scope.citadel = citadel;
                $scope.menu_expanded = false;
                $scope.currentView = "Buildings";
            }
        }
    });
})();