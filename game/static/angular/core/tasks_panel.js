(function() {
    var app = angular.module('game');

    var tasksVersion = 0;

    var missions = {
        LearnTheInterface: {
            Panels: function(task, $rootScope, $state, $scope) {
                return;
                var left_panels = $("#user-panel").add("#ship-panel");
                var panels = this;

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
                    $state.go("map");
                    $("#details-panel").hide();
                }

                if(panels.listener_system_click === undefined && task.state === "click_any_system") {
                    panels.listener_system_click = $rootScope.$on('$stateChangeSuccess', function(event, toState) {
                        if($state.includes('map.system')) {
                            if($state.includes('map.system.planet')) {
                                $scope.task_action('planet');
                            }
                            else {
                                $scope.task_action('star');
                            }
                            $("#details-panel").show();
                            panels.listener_system_click();
                        }
                    });
                }

                function handle(task, state, elements, event, version) {
                    var handler = function (){
                        if(tasksVersion === version) {
                            console.log(task, event, elements);
                            $scope.task_action('acknowledge');
                        }
                    };

                    if(task.state === state) {
                        $("body").on(event, elements, handler);
                    }
                }

                handle(task, "left_panels", "#user-panel", 'mouseenter', tasksVersion);
                handle(task, "left_panels", "#ship-panel", 'mouseenter', tasksVersion);
                handle(task, "close_details", "a#details-panel-close", 'click', tasksVersion);
                handle(task, "map", "a#map-reset", 'click', tasksVersion);
            }
        },
        UpgradeYourShip: {
            FirstScan: function (task, $rootScope, $state, $scope) {
                var firstScan = this;
                $(".extract-resources").hide();
                if(firstScan.listener_resources_click === undefined && task.state === "started") {
                    firstScan.listener_resources_click = $rootScope.$on('$stateChangeSuccess', function(event, toState) {
                        if($state.includes('map.system.planet.resources')) {
                            $scope.task_action('acknowledge');
                            firstScan.listener_resources_click();
                        }
                    });
                }
            },
            Extraction: function (task, $rootScope, $state, $scope) {
                $(".extract-resources").show();
            }
        }
    };

    app.directive('coreTasksPanel', function() {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/tasks_panel.html',
            scope: {
            },
            controller: function($rootScope, $state, $scope, $http, $window, account, currentShip) {
                $scope.updatedTasks = {};
                $scope.account = account;
                $scope.currentShip = currentShip;

                function activateTasks(tasks) {
                    tasksVersion += 1;
                    $.each(tasks, function (index, task) {
                        if(missions[task.mission] !== undefined && missions[task.mission][task.type] !== undefined) {
                            missions[task.mission][task.type](task, $rootScope, $state, $scope ); //TODO to many parameters...
                        }
                    });
                }

                $scope.setCurrentTask = function(i) {
                    $scope.currentTask = $scope.tasks[i];
                    delete $scope.updatedTasks[$scope.currentTask.id];
                    $scope.status = {};
                };

                function updateCurrentTask() {
                    var updated = false;
                    //search same task (by id)
                    $.each($scope.tasks, function(i, task){
                        if(task.id == $scope.currentTask.id) {
                            $scope.currentTask = task;
                            updated = true;
                        }
                    });
                    if(updated) {
                        return;
                    }
                    //if not found, then find another task from the same mission
                    $.each($scope.tasks, function(i, task){
                        if(task.mission == $scope.currentTask.mission) {
                            $scope.currentTask = task;
                            updated = true;
                        }
                    });
                    if(updated) {
                        return;
                    }
                    //fallback to first task on the list
                    $scope.setCurrentTask(0);
                }

                $scope.isUpdated = function(task_id) {
                    return $scope.updatedTasks[task_id];
                };

                var subscription = connection.create_subscription('tasks', function (data) {
                    $scope.tasks = data.tasks;
                    $scope.updatedTasks[data.updated_task] = true;
                    if(data.archived) {
                        $window.ga('send', 'event', 'task', 'archived', data.type);
                    }
                    //$scope.updatedTasks[10] = true;//TODO
                    updateCurrentTask();
                    activateTasks($scope.tasks);
                    $scope.$digest();
                });

                $http.get("/api/core/tasks/").success(function(data) {
                    $scope.tasks = data.results;
                    if($scope.tasks.length > 0) {
                        $scope.setCurrentTask(0);
                    }
                    activateTasks($scope.tasks);
                    subscription.subscribe(account.id);
                });

                $scope.task_action = function(type, params) {
                    if(params !== undefined) {
                        params['type'] = type;
                    }
                    else {
                        params = {type: type}
                    }
                    $scope.status.message = "validating response...";
                    $scope.status.error = false;
                    $http.post("/api/core/tasks/"+$scope.currentTask.id+"/action/", params).success(function() {
                        $scope.status.message = "";
                        $scope.error = false;
                    }).error(function(data) {
                        $scope.status.message = data;
                        $scope.status.error = true;
                    });
                }
            }
        }
    });
})();