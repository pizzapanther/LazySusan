
var lslist = angular.module('lslist', ['ngCookies', 'ngSanitize', 'ui.bootstrap']);

var FilterModalInstanceCtrl = function ($scope, $modalInstance, filters) {
  $scope.form = {
    which: '',
    include: 'default-filter.html',
    value: ""
  };
  
  $scope.filters = filters;
  
  $scope.update_form = function () {
    if ($scope.form.which === '') {
      $scope.form.include = 'default-filter.html';
    }
    
    else {
      $scope.form.include = 'filter-' + $scope.form.which.attribute + '.html';
    }
  };
  
  $scope.add = function () {
    if (!$scope.form.value) {
      alert('Please choose a value to filter on.');
      return null;
    }
    
    var url = location.pathname;
    var pair = $scope.form.which.attribute + '=' + encodeURIComponent($scope.form.value);
    if (location.search) {
      url += location.search + '&' + pair;
    }
    
    else {
      url += '?' + pair;
    }
    
    location.href = url;
  };

  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
};

lslist.controller('FilterCtrl', function($scope, $rootScope, $modal, $templateCache) {
  for (var i=0; i < FILTERS.length; i++) {
    var f = FILTERS[i];
    $templateCache.put('filter-' + f.attribute + '.html', f.template);
  }
  
  $scope.add_filter = function () {
    var modalInstance = $modal.open({
      templateUrl: ng_template_url('filterModal.html'),
      windowClass: 'filterModal',
      controller: FilterModalInstanceCtrl,
      resolve: {
        filters: function () { return FILTERS; }
      }
    });
    
  };
});