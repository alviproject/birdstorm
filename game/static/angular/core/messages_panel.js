(function() {
    var app = angular.module('game');

    app.directive('coreMessagesPanel', function() {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/messages_panel.html',
            scope: {
                accountData: "=accountData"
            },
            link: function(scope, element) {
                scope.messages = [];
                scope.subscription_actions = connection.create_subscription('messages', function (data) {
                    scope.messages.push(data.message);
                    scope.$apply();
                });

                //accountData may be not available at this stage, so let's wait until it is
                scope.$watch('accountData.id', function(newID, oldID){
                    if(newID) {
                        scope.subscription_actions.subscribe(newID);
                    }
                });
            }
        }
    });
})();