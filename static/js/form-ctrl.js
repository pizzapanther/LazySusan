
function ng_template_url (tpl) {
  return NG_TEMPLATE_URL.slice(0, NG_TEMPLATE_URL.length - 1) + tpl;
}

var lsform = angular.module('lsform', ['ngCookies', 'ui.bootstrap']);

lsform.run(['$http', '$cookies', function ($http, $cookies) {
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
  }]
);

lsform.controller('FormCtrl', function($scope, $rootScope) {
  
});