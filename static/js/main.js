const fetchMapData = () =>
  Promise.all([
    fetch('/static/final_rides.json').then(res => res.json()),
    fetch('/static/final_segments.json').then(res => res.json()),
  ]);

const renderMap = (map, rides, segments) => {
  const rideById = {};

  rides.forEach(ride => {
    const path = google.maps.geometry.encoding.decodePath(ride.path);
    const poly = new google.maps.Polyline(visiblePolyOptions);

    poly.setMap(map);
    poly.setPath(path);

    rideById[ride.id] = ride;
  });

  segments.forEach(segment => {
    const path = google.maps.geometry.encoding.decodePath(segment.path);
    const poly = new google.maps.Polyline(invisiblePolyOptions);

    poly.setMap(map);
    poly.setPath(path);

    google.maps.event.addListener(poly, 'click', event => {
      UI.toggleList(true);

      const segmentRides = segment.ride_ids.map(ride_id => rideById[ride_id]);
      UI.renderList(segmentRides);
    });
  });

  setupMouseOver(map, rideById);
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

const initialize = () => {
  const styledMapType = new google.maps.StyledMapType(map_style);
  const map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

  map.mapTypes.set('styled_map', styledMapType);
  map.setMapTypeId('styled_map');

  map.addListener(
    'bounds_changed',
    utils.debounce(() => {
      location.hash = utils.url.objectToUrlParams(utils.positionTools.serializePosition(map));
    }, 100)
  );

  fetchMapData().then(([rides, segments]) => {
    renderMap(map, rides, segments);
  });
};

const UI = {
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

  toggleContacts(shouldShow) {
    const contactsElement = document.querySelector('#contactsLayer');
    contactsElement.classList.toggle('contactsLayer--hidden', !shouldShow);
  },

  toggleList(shouldShow) {
    const listElement = document.querySelector('.vidlist');
    listElement.classList.toggle('vidlist--hidden', !shouldShow);
    listElement.classList.toggle('vidlist--open', shouldShow);
  },
};

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

try {
  const position = utils.url.urlParamsToObject(location.hash.slice(1));
  Object.assign(mapOptions, utils.positionTools.deserializePosition(position));
} catch (e) {
  console.log('Unable to deserialize', e);
}

google.maps.event.addDomListener(window, 'load', initialize);
