let map = null;

const state = {};

const fetchMapData = () =>
  Promise.all([
    fetch('/static/final_rides.json').then(res => res.json()),
    fetch('/static/final_segments.json').then(res => res.json()),
  ]);

const renderMap = (map, rides, segments) => {
  utils.asyncForEach(rides, ride => {
    const path = google.maps.geometry.encoding.decodePath(ride.path);
    const poly = new google.maps.Polyline(visiblePolyOptions);

    poly.setMap(map);
    poly.setPath(path);

    google.maps.event.addListener(poly, 'click', event => {
      router.updateHash({ path: ride.segment_path });
    });
  });
};

const setupMouseOver = (map, rideById) => {
  const polyHighlight = new google.maps.Polyline(redPolyOptions);
  document.addEventListener('mouseover', event => {
    const element = event.target.closest('[data-ride-id]');

    if (element) {
      const ride = rideById[element.dataset.rideId];
      const ridePath = google.maps.geometry.encoding.decodePath(ride.path);

      polyHighlight.setPath(ridePath);
      polyHighlight.setMap(map);
    } else {
      polyHighlight.setMap(null);
    }
  });
};

const initializeMap = () => {
  const styledMapType = new google.maps.StyledMapType(map_style);
  map = new google.maps.Map(
    document.getElementById('map-canvas'),
    Object.assign({}, mapOptions, utils.positionTools.deserializePosition(router.getParams()))
  );

  map.mapTypes.set('styled_map', styledMapType);
  map.setMapTypeId('styled_map');

  map.addListener(
    'bounds_changed',
    utils.debounce(() => {
      const { lat, lng, zoom } = utils.positionTools.serializePosition(map);

      router.updateHash({ lat, lng, zoom });
    }, 100)
  );

  fetchMapData().then(([rides, segments]) => {
    const rideById = {};

    state.rideById = rideById;
    rides.forEach(ride => {
      rideById[ride.id] = ride;
    });

    segments.forEach(segment => {
      segment.ride_ids.forEach(ride_id => {
        rideById[ride_id].segment_path = segment.path;
      });
    });

    state.segments = segments;
    state.rides = rides;

    renderMap(map, rides, segments);

    UI.setupEvents();
    setupMouseOver(map, rideById);

    router.init();
  });
};

const UI = {
  toggleMap(shouldBeInteractive) {
    map.setOptions({
      draggable: shouldBeInteractive,
      zoomControl: shouldBeInteractive,
      scrollwheel: shouldBeInteractive,
      disableDoubleClickZoom: !shouldBeInteractive,
    });
  },

  renderVideo(rideId) {
    console.log('Render', rideId);
    document.querySelector('.js-video-wrapper').innerHTML = `
      <iframe
        width="100%"
        height="480"
        src="http://www.youtube.com/embed/${rideId}?autoplay=1"
        frameborder="0"
        allowfullscreen
        >
      </iframe>
    `;
  },

  renderList(rides) {
    document.querySelector('#listid').innerHTML = rides
      .map(
        ({ video, from, to, id }) => `
        <a href="${video.url}" target="_blank" data-ride-id="${id}">
          <li>
            <div class="image">
              <img src="${video.thumb}" height="150" width="200">
              <div class="description">
                <p class="description_content">${utils.numberToHHMMSS(video.duration)}</p>
              </div>
            </div>
            <h3>${from.name} - ${to.name}</h3>
            <p>${video.title}</p>
          </li>
        </a>
      `
      )
      .join('\n');
  },

  toggleVideo(shouldShow) {
    this.toggleMap(!shouldShow);

    document.body.classList.toggle('is-video', shouldShow);

    const element = document.querySelector('.video-view');
    element.classList.toggle('popup--hidden', !shouldShow);

    if (!shouldShow) {
      element.querySelector('.js-video-wrapper').innerHTML = '';
    }
  },

  toggleContacts(shouldShow) {
    const contactsElement = document.querySelector('#contactsLayer');
    contactsElement.classList.toggle('contactsLayer--hidden', !shouldShow);
  },

  toggleList(shouldShow) {
    const listElement = document.querySelector('.vidlist');
    listElement.classList.toggle('vidlist--hidden', !shouldShow);
    listElement.classList.toggle('vidlist--open', shouldShow);
  },

  setupEvents() {
    document.querySelector('.open').addEventListener('click', () => {
      UI.toggleList(true);
    });

    document.querySelector('.close').addEventListener('click', () => {
      UI.toggleList(false);
    });

    document.querySelector('#info').addEventListener('click', () => {
      UI.toggleContacts(true);
    });

    document.querySelector('#cross').addEventListener('click', () => {
      UI.toggleContacts(false);
    });

    document.querySelector('.js-video-back').addEventListener('click', event => {
      event.preventDefault();
      UI.toggleVideo(false);
      router.updateHash({ ride: '' });
    });

    window.addEventListener('click', event => {
      const element = event.target.closest('[data-ride-id]');
      if (element) {
        event.preventDefault();
        router.updateHash({ ride: element.dataset.rideId });
      }
    });
  },
};

const router = {
  getParams() {
    return utils.url.urlParamsToObject(location.hash.slice(1));
  },

  updateHash(obj) {
    try {
      const currentObj = this.getParams();
      location.hash = utils.url.objectToUrlParams(Object.assign({}, currentObj, obj));
    } catch (e) {
      location.hash = utils.url.objectToUrlParams(obj);
    }
  },

  _navigate() {
    console.log('_navigate');
    try {
      const params = this.getParams();

      if (params.ride) {
        UI.toggleVideo(true);
        UI.renderVideo(params.ride);
        return;
      }

      if (params.path) {
        UI.toggleList(true);

        const segment = state.segments.find(segment => segment.path === params.path);
        const segmentRides = segment.ride_ids.map(ride_id => state.rideById[ride_id]);

        UI.renderList(segmentRides);
        return;
      }
    } catch (e) {
      console.log('Unable to deserialize', e);
    }
  },

  init() {
    window.addEventListener('hashchange', this._navigate.bind(this));
    this._navigate();
  },
};

google.maps.event.addDomListener(window, 'load', initializeMap);
