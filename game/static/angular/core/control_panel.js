(function() {
    var app = angular.module('game');

    app.controller('ControlPanelController', ['$http', function($http) {
        var controlPanel = this;
        controlPanel.ships = [];
        $http.get("/api/core/own_ships").success(function(data, status, headers, config){
            controlPanel.ships = data.results;
            controlPanel.currentShip = controlPanel.ships[0];

            // at this stage we shall aready have scope.accountData loaded, se we can connect to profile channel
            //TODO use service
            connection.add_channel('profile.' + scope.accountData.id, function (data) {
                console.log(data);
            });
        });
    }]);

    app.directive('coreControlPanel', function () {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/control_panel.html',
            scope: {
                map: '=map',
                controlPanel: '=controlPanel',
                accountData: '=accountData'
            },
            link: function(scope, element) {
                scope.scan = function (planet_id) {
                    var ship_id = this.controlPanel.currentShip.id;
                    $http.post('/api/core/own_ships/'+ship_id+'/scan/', {
                        planet_id: planet_id
                    });
                }
            }
        }
    });
})();