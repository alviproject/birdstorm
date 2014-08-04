(function() {
    var app = angular.module('game');

    app.controller('ContextPanelController', [function() {
        var contextPanel = this;
        this.switch = function (choice, data) {
            contextPanel.choice = choice;
            //set basic data, extended data will be requested
            contextPanel.data = data;

            var injector = angular.element(document).injector();
            var $http = injector.get('$http');
            $http.get("/api/core/"+choice+"s/"+data.id+"/")
                .success(function (data, status, headers, config) {
                    //set extended data
                    contextPanel.data = data;
            });
        }
    }]);

    app.directive('coreContextPanel', function($http) {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/context_panel.html',
            scope: {
                contextPanel: '=contextPanel',
                controlPanel: '=controlPanel',
                detailsPanel: '=detailsPanel'
            },
            link: function(scope, element) {
                scope.go_to_system = function (system_id) {
                    var ship_id = this.controlPanel.currentShip.id;
                    $http.post('/api/core/own_ships/'+ship_id+'/move/', {
                        system_id: system_id
                    });
                }
            }
        }
    });
})();