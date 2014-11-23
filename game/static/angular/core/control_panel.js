(function() {
    var app = angular.module('game');

    app.directive('coreControlPanel', function ($http, currentShip, account) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/control_panel.html',
            scope: {
                map: '=map'
            },
            controller: function($scope) {
            }
        }
    });
})();