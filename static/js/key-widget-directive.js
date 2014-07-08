var TEMPLATES = {};
var LOADED_JS = [];

var FilterModalInstanceCtrl = function ($scope, $modalInstance, kind, filters, parentScope) {
  $scope.form = {
    which: '',
    include: 'default-filter.html',
    value: ""
  };
  
  $scope.filters = filters;
  $scope.kind = kind;
  
  $scope.update_form = function () {
    if ($scope.form.which === '') {
      $scope.form.include = 'default-filter.html';
    }
    
    else {
      $scope.form.include = $scope.kind + '-filter-' + $scope.form.which.attribute + '.html';
      $scope.process('init_widget')($scope);
    }
  };
  
  $scope.process = function (fname) {
    var defaultf = {
      init_widget: function (scope) {},
      get_value: function (scope) { return scope.form.value; }
    };
    
    var f = null;
    if ($scope.form.which !== '' && $scope.form.which.function_namespace) {
      f = window[$scope.form.which.function_namespace];
    }
    
    if (f && f[fname]) {
      return f[fname];
    }
    
    return defaultf[fname]
  };
  
  $scope.add = function () {
    if (!$scope.form.value) {
      alert('Please choose a value to filter on.');
      return null;
    }
    
    var value = $scope.process('get_value')($scope);
    parentScope.apply_filter({
      param: $scope.form.which.attribute,
      value: value
    });
    
    $modalInstance.dismiss('added');
  };

  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
};

var SearchModalInstanceCtrl = function ($scope, $http, $modalInstance, $templateCache, $modal, kind, widget) {
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
    has_prev: false,
    filters: [],
    applied_filters: [],
    js: []
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
  
  $scope.submit = function (page) {
    var payload = {
      search: $scope.lookup.search,
      kind: $scope.lookup.kind,
      filters: $scope.lookup.applied_filters
    };
    
    if (page) {
      if (page == 'use-cache') {
        payload.use_cache = true;
      }
      
      else {
        $scope.lookup.page = page;
      }
    }
    
    $http.post(KIND_LOOKUP_URL + '?page=' + $scope.lookup.page, payload)
      .success(function(data, status, headers, config) {
        if (data.status == 'OK') {
          $scope.lookup.message = '';
          $scope.lookup.results = data.results;
          $scope.lookup.headers = data.headers;
          $scope.lookup.page = data.page;
          $scope.lookup.total_pages = data.total_pages;
          $scope.lookup.has_next = data.has_next;
          $scope.lookup.has_prev = data.has_prev;
          $scope.lookup.filters = data.filters;
          $scope.lookup.applied_filters = data.applied_filters;
          $scope.lookup.js = data.js;
          $scope.lookup.search = data.search;
          
          for (var i=0; i < data.filters.length; i++) {
            var filter = data.filters[i];
            var tpl_id = $scope.lookup.kind + '-filter-' + filter.attribute + '.html';
            if (TEMPLATES[tpl_id]) {}
            else {
              $templateCache.put(tpl_id, filter.template);
              TEMPLATES[tpl_id] = true;
            }
          }
          
          for (var i=0; i < data.js.length; i++) {
            var files = data.js[i].files;
            for (var j=0; j < files.length; j++) {
              if (LOADED_JS.indexOf(files[j]) < 0) {
                $.getScript(files[j]);
                LOADED_JS.push(files[j]);
              }
            }
          }
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
  
  $scope.add_filter = function () {
    var modalInstance = $modal.open({
      templateUrl: ng_template_url('filterModal.html'),
      windowClass: 'filterModal',
      controller: FilterModalInstanceCtrl,
      resolve: {
        filters: function () { return $scope.lookup.filters; },
        kind: function () { return $scope.lookup.kind; },
        parentScope: function () { return $scope }
      }
    });
  };
  
  $scope.apply_filter = function (filter) {
    $scope.lookup.applied_filters.push(filter);
    $scope.submit(1);
  };
  
  $scope.remove_all_filters = function () {
    $scope.lookup.applied_filters = [];
    $scope.lookup.search = "";
    $scope.submit(1);
  };
  
  $scope.remove_filter = function (index) {
    $scope.lookup.applied_filters.splice(index, 1);
    $scope.submit(1);
  }
  
  $scope.submit('use-cache');
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
