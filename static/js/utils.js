var utils = {
  debounce: function(func, wait, immediate) {
    var timeout;
    return function() {
      var context = this,
        args = arguments;
      var later = function() {
        timeout = null;
        if (!immediate) func.apply(context, args);
      };
      var callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func.apply(context, args);
    };
  },
  url: {
    objectToUrlParams: function(obj) {
      return Object.keys(obj).map(key => key + '=' + encodeURIComponent(obj[key])).join('&');
    },
    urlParamsToObject: function(params) {
      return params.split('&').reduce((acc, keyValue) => {
        var parts = keyValue.split('=');
        acc[parts[0]] = parts[1];
        return acc;
      }, {});
    },
  },
};
