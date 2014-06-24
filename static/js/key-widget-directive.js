
var SearchModalInstanceCtrl = function ($scope, $http, $modalInstance, kind, widget) {
  $scope.lookup = {
    kind: kind,
    widget: widget,
    results: [],
    headers: [],
    search: '',
    message: '',
    page: 1,
    total_pages: 0,
    has_next: false,
    has_prev: false
  };
  
  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
  
  $scope.prev_page = function () {
    $scope.lookup.page = $scope.lookup.page - 1;
    $scope.submit();
  };
  
  $scope.next_page = function () {
    $scope.lookup.page = $scope.lookup.page + 1;
    $scope.submit();
  };
  
  $scope.submit = function () {
    $http.post(KIND_LOOKUP_URL + '?page=' + $scope.lookup.page, {search: $scope.lookup.search, kind: $scope.lookup.kind})
      .success(function(data, status, headers, config) {
          if (data.status == 'OK') {
            $scope.lookup.message = '';
            $scope.lookup.results = data.results;
            $scope.lookup.headers = data.headers;
            $scope.lookup.page = data.page;
            $scope.lookup.total_pages = data.total_pages;
            $scope.lookup.has_next = data.has_next;
            $scope.lookup.has_prev = data.has_prev;
          }
          
          else {
            $scope.lookup.message = data.message;
          }
      });
  };
  
  $scope.select = function (key, name) {
    $("#name_" + $scope.lookup.widget).html(name);
    $("#" + $scope.lookup.widget).val(key);
    
    $modalInstance.dismiss('selected');
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
