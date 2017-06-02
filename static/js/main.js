var lastInfoWindow = null

function initialize() {

    var mapOptions = {
        center: { lat: 50.912262, lng: 8.512218},
        scrollwheel: true,
        zoom: 6,
        disableDefaultUI: true
    }

    var polyOptions = {
        strokeColor: '#0a0175',
        strokeOpacity: 0.3,
        strokeWeight: 6
    }

    console.log(document.getElementById("header"))

    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    $.ajax({
        url: "/static/test_data.json",
        dataType: "json",
        success: function(data){
            var routes = data["routes"]
            for (var i = 0; i < routes.length; i++) {
                var route = routes[i]
                var path = google.maps.geometry.encoding.decodePath(route["path"])
                var poly = new google.maps.Polyline(polyOptions)

                poly.setMap(map)
                poly.setPath(path)

                attachWindow(map, poly, route)
            }
        }
    })
}

function attachWindow(map, poly, route) {
    google.maps.event.addListener(poly, 'click', function(event) {
        // if (lastInfoWindow != null) {
        //     lastInfoWindow.close()
        // }

        // var infowindow = new google.maps.InfoWindow({
        //     content: content,
        //     position: event.latLng,
        //     map: map
        // })

        // lastInfoWindow = infowindow

        var parent = $("<div/>")
        var list =$("<ul/>", {"class":"listbox"})

        for (var i = 0; i < 2; i++) {
            var elem = $("<li/>")
                .append($("<img/>", {"src":route["video"]["thumb"]}))
                .append($("<h3/>").text("Amsterdam - Paris"))
                .append($("<p/>").text(route["video"]["title"]))

            list.append(elem)
        }
        parent.append(list)

        console.log(parent.html())

        var myOptions = {
            content: parent.html(),
            position: event.latLng,
            closeBoxMargin: "10px 4px 4px 4px",
            closeBoxURL: '/static/cross6.png',
            boxStyle: { 
                background: "url('static/transparent.png')"
            }
        };

        var ib = new InfoBox(myOptions);
        ib.open(map);
        console.log(ib)
    })   

}

google.maps.event.addDomListener(window, 'load', initialize);