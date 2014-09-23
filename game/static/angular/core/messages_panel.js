(function() {
    var app = angular.module('game');

    app.directive('coreMessagesPanel', function() {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/messages_panel.html',
            scope: {
            }
        }
    });
})();