(function() {
    var app = angular.module('game');

    app.directive('coreTasksPanel', function() {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/tasks_panel.html',
            scope: {
            }
        }
    });
})();