
var lsform = angular.module('lsform', ['ngCookies', 'ngSanitize', 'ui.bootstrap']);

lsform.run(['$http', '$cookies', function ($http, $cookies) {
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
  }]
);

lsform.controller('FormCtrl', function($scope, $rootScope) {
  
});