(function() {
    //TODO rename this panel
    var app = angular.module('game');

    app.directive('coreMessagesPanel', function() {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/messages_panel.html',
            scope: {
            },
            controller: function($scope, $http, account) {
                $scope.messages = [];
                $scope.subscription_actions = connection.create_subscription('messages', function (data) {
                    $scope.messages.push(data.message);
                    if($scope.messages.length > 10) {
                        $scope.messages.shift();
                    }
                    $scope.$apply();
                });

                //account may be not available at this stage, so let's wait until it is
                $scope.account = account;
                $scope.$watch('account.id', function(){
                    if(account.id !== undefined) {
                        $scope.subscription_actions.subscribe(account.id);
                    }
                });
                $scope.nextTurn = function() {
                    $http.post("/api/core/base/next_turn/").success(function() {
                    });
                }
            }
        }
    });
})();
