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
      return Object.keys(obj)
        .map(key => {
          if (key && obj[key]) {
            return key + '=' + encodeURIComponent(obj[key]);
          }
          return '';
        })
        .join('&');
    },
    urlParamsToObject: function(params) {
      if (params.length === 0) {
        return {};
      }

      return params.split('&').reduce((acc, keyValue) => {
        var parts = keyValue.split('=');
        if (parts.length === 2) {
          acc[parts[0]] = decodeURIComponent(parts[1]);
        }
        return acc;
      }, {});
    },
  },
  numberToHHMMSS: function(number) {
    var sec_num = parseInt(number, 10); // don't forget the second param
    var hours = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - hours * 3600) / 60);
    var seconds = sec_num - hours * 3600 - minutes * 60;

    if (hours < 10) {
      hours = '0' + hours;
    }
    if (minutes < 10) {
      minutes = '0' + minutes;
    }
    if (seconds < 10) {
      seconds = '0' + seconds;
    }
    var time = hours + ':' + minutes + ':' + seconds;
    return time;
  },
  positionTools: {
    serializePosition: map => {
      const center = map.getCenter();
      const position = { lat: center.lat(), lng: center.lng(), zoom: map.getZoom() };
      return position;
    },
    deserializePosition: obj => {
      if (!obj.lat || !obj.lng || !obj.zoom) {
        return null;
      }

      return {
        center: { lat: parseFloat(obj.lat), lng: parseFloat(obj.lng) },
        zoom: Number(obj.zoom),
      };
    },
  },
  requestIdleCallback(callback) {
    // poor man's polyfill
    if (window.requestIdleCallback) {
      return window.requestIdleCallback(callback);
    } else {
      return setTimeout(callback, 0);
    }
  },
  asyncForEach(arr, callback, batchSize = 25) {
    /*
      Same as Array.prototype.forEach, but takes a pause after
      %batchSize% elements.
    */
    const inner = currentIndex => {
      callback(arr[currentIndex], currentIndex, arr);

      if (currentIndex === arr.length - 1) {
        return;
      }

      if (currentIndex % batchSize === 0) {
        this.requestIdleCallback(() => {
          inner(currentIndex + 1);
        });
      } else {
        inner(currentIndex + 1);
      }
    };

    inner(0);
  },
};
