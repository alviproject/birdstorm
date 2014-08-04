(function() {
    var app = angular.module('game');

    app.directive('chat', function ($http) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/chat.html',
            scope: {
            },
            link: function (scope, element) {
                var chat = {};
                scope.chat = chat;

                chat.messages = [];
                chat.text = "";

                //
                //retrieve chat messages
                //
                $http.get("/api/chat/messages").success(function(data, status, headers, config){
                    chat.messages = data.results.reverse();
                });

                //
                //connect to chat
                //
                connection.add_channel('chat.general_room', function (data) {
                    chat.messages.push(data);
                    scope.$apply();
                    var chatPanel = $("#chat-panel");
                    chatPanel.scrollTop(chatPanel[0].scrollHeight);
                });

                //
                //send a new chat message
                //
                chat.send = function() {
                    if(chat.text == "") {
                        return
                    }
                    $http.post("/api/chat/messages/", {text: chat.text});
                    chat.text = "";
                };
            }
        }
    });
})();

