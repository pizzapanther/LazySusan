
lsform.directive('listWidget', function() {
  function link (scope, element, attrs) {
    scope.list = [];
    for (var i in scope.values) {
      scope.list.push({value: scope.values[i]});
    }
    
    scope.add_value = function () {
      scope.list.push({value: ''});
    };
    
    scope.rm_value = function (index) {
      scope.list.splice(index, 1);
    };
  }
  
  return {
    restrict: 'E',
    link: link,
    template: '<a class="btn clickme" ng-click="add_value()"><i class="fa fa-plus"></i></a>\
    <ul id="{{ wid }}" class="list-widget">\
      <li ng-repeat="v in list">\
        <ng-include src="wid + \'.tpl\'"></ng-include>\
        <a class="rm btn clickme" ng-click="rm_value($index)"><i class="fa fa-times-circle"></i></a>\
      </li>\
    </ul>',
    scope: {
      wid: '=',
      values: '='
    }
  };
});