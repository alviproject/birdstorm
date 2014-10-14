(function() {
    var app = angular.module('game');

    var missions = {
        LearnTheInterface: {
            Panels: function(task, $rootScope, $state, $scope) {
                var left_panels = $("#user-panel").add("#ship-panel");

                if(task.state === "started"
                    || task.state === "click_any_system"
                    || task.state === "planet_not_star"
                    || task.state === "star_system") {
                    left_panels.hide();
                }
                else {
                    left_panels.show();
                }

                if(task.state === "started" || task.state === "click_any_system") {
                    $("#details-panel").hide();
                }

                if(this.listener_system_click === undefined && task.state === "click_any_system") {
                    this.listener_system_click = $rootScope.$on('$stateChangeSuccess', function(event, toState) {
                        if(task.state === "click_any_system" && $state.includes('map.system')) {
                            if($state.includes('map.system.planet')) {
                                $scope.task_action('planet');
                            }
                            else {
                                $scope.task_action('star');
                            }
                            $("#details-panel").show();
                        }
                    });
                }

                var acknowledge_handler = function (){
                    $scope.task_action('acknowledge');
                };

                if(this.left_panels_mouser_over_set === undefined && task.state === "left_panels") {
                    this.left_panels_mouser_over_set = true;
                    left_panels.one('mouseenter', acknowledge_handler);
                }

                if(this.details_panel_close_set === undefined && task.state === "close_details") {
                    this.details_panel_close_set = true;
                    $("a#details-panel-close").one('click', acknowledge_handler);
                }

                if(this.refresh_map_set === undefined && task.state === "map") {
                    this.refresh_map_set = true;
                    $("a#map-reset").one('click', acknowledge_handler);
                }
            }
        }
    };

    app.directive('coreTasksPanel', function() {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/tasks_panel.html',
            scope: {
            },
            controller: function($rootScope, $state, $scope, $http, account) {
                $scope.currentTaskIndex = 0;
                $scope.updatedTasks = {};

                function activateTasks(tasks) {
                    $.each(tasks, function (index, task) {
                        missions[task.mission][task.type](task, $rootScope, $state, $scope ); //TODO to many parameters...
                    });
                }

                $scope.setCurrentTask = function(i) {
                    $scope.currentTaskIndex = i < $scope.tasks.length ? i : 0;
                    $scope.currentTask = $scope.tasks[$scope.currentTaskIndex];
                    delete $scope.updatedTasks[$scope.currentTask.id];
                };

                $scope.isUpdated = function(task_id) {
                    return $scope.updatedTasks[task_id];
                };

                var subscription = connection.create_subscription('tasks', function (data) {
                    $scope.tasks = data.tasks;
                    $scope.updatedTasks[data.updated] = true;
                    $scope.updatedTasks[10] = true;
                    $scope.setCurrentTask($scope.currentTaskIndex);
                    activateTasks($scope.tasks);
                    $scope.$digest();
                });

                $http.get("/api/core/tasks/").success(function(data) {
                    $scope.tasks = data.results;
                    $scope.setCurrentTask(0);
                    activateTasks($scope.tasks);
                    subscription.subscribe(account.id);
                });

                $scope.task_action = function(type) {
                    $http.post("/api/core/tasks/"+$scope.currentTask.id+"/action/", {
                        type: type
                    });
                }
            }
        }
    });
})();