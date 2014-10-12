(function() {
    var app = angular.module('game');

    app.directive('coreTasksPanel', function() {
        return {
            restrict: 'E',
            templateUrl: '/static/angular/core/tasks_panel.html',
            scope: {
            },
            controller: function($scope, $http, account) {
                $scope.currentTaskIndex = 0;
                $scope.updatedTasks = {};

                function setCurrentTask(i) {
                    $scope.currentTaskIndex = i < $scope.tasks.length ? i : 0;
                    $scope.currentTask = $scope.tasks[$scope.currentTaskIndex];
                    delete $scope.updatedTasks[$scope.currentTask.id];
                }

                $scope.setCurrentTask = setCurrentTask;
                $scope.isUpdated = function(task_id) {
                    return $scope.updatedTasks[task_id];
                };

                var subscription = connection.create_subscription('tasks', function (data) {
                    $scope.tasks = data.tasks;
                    $scope.updatedTasks[data.updated] = true;
                    $scope.updatedTasks[10] = true;
                    setCurrentTask($scope.currentTaskIndex);
                    $scope.$digest();
                });

                $http.get("/api/core/tasks/").success(function(data) {
                    $scope.tasks = data.results;
                    setCurrentTask(0);
                    subscription.subscribe(account.id);
                });
            }
        }
    });
})();