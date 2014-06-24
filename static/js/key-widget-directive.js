
var SearchModalInstanceCtrl = function ($scope, $http, $modalInstance, kind, widget) {
  $scope.lookup = {
    kind: kind,
    widget: widget,
    results: [],
    headers: [],
    search: '',
    message: ''
  };
  
  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
  
  $scope.submit = function () {
    $http.post(KIND_LOOKUP_URL, {search: $scope.lookup.search, kind: $scope.lookup.kind})
      .success(function(data, status, headers, config) {
          if (data.status == 'OK') {
            $scope.lookup.message = '';
            $scope.lookup.results = data.results;
            $scope.lookup.headers = data.headers;
          }
          
          else {
            $scope.lookup.message = data.message;
          }
      });
  };
  
  $scope.submit();
};

lsform.directive('keyLookup', function($modal) {
  function link (scope, element, attrs) {
    scope.show_search = function () {
      var modalInstance = $modal.open({
        templateUrl: ng_template_url('KindSearchModal.html'),
        controller: SearchModalInstanceCtrl,
        size: 'lg',
        windowClass: 'lookupModal',
        resolve: {
          kind: function () { return scope.kind; },
          widget: function () { return scope.widget; }
        }
      });
    };
  }
  
  return {
    restrict: 'E',
    link: link,
    template: '<a ng-click="show_search()" class="btn btn-default"><i class="fa fa-search"></i></a>',
    scope: {
      kind: '@',
      widget: '@'
    }
  };
});
