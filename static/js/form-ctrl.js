
var lsform = angular.module('lsform', ['ngCookies', 'ngSanitize', 'ui.bootstrap']);

lsform.run(['$http', '$cookies', function ($http, $cookies) {
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
  }]
);

lsform.controller('FormCtrl', function($scope, $rootScope, $compile) {
  $scope.add_structured = function (prefix, auto_id) {
    var prefix_id = auto_id.replace('%s', prefix);
    
    var total_forms = parseInt($("#" + prefix_id + '-TOTAL_FORMS').val());
    var max_forms = parseInt($("#" + prefix_id + '-MAX_NUM_FORMS').val());
    if (total_forms + 1 > max_forms) {
      alert('You can not add any more forms.');
    }
    
    else {
      total_forms = total_forms + 1;
      var tpl = document.querySelector('#' + prefix + '-empty-html');
      var new_content = tpl.innerHTML.replace(/__prefix__/g, total_forms - 1);
      
      var elem = $compile(new_content)($scope);
      
      $("#" + prefix + "-insert-before").before(elem);
      $("#" + prefix_id + '-TOTAL_FORMS').val(total_forms);
    }
  };
});