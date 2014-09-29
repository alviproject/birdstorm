(function() {
    var app = angular.module('game');

    app.directive('coreMessagesPanel', function() {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/messages_panel.html',
            scope: {
            },
            controller: function($scope, account) {
                $scope.messages = [];
                $scope.subscription_actions = connection.create_subscription('messages', function (data) {
                    $scope.messages.push(data.message);
                    $scope.$apply();
                });

                //account may be not available at this stage, so let's wait until it is
                $scope.account = account;
                $scope.$watch('account.id', function(){
                    $scope.subscription_actions.subscribe(account.id);
                });
            }
        }
    });
})();