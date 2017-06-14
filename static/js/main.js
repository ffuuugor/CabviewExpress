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

    var polyOptions2 = {
        strokeColor: '#0a0175',
        strokeOpacity: 0,
        strokeWeight: 6
    }

    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    $(document).on("mouseenter", ".infoBox", function(){
        map.setOptions( {scrollwheel:false} ); 
    })

    $(document).on("mouseleave", ".infoBox", function(){
        map.setOptions( {scrollwheel:true} ); 
    })

    $(document).on("closeclick", function(){
        console.log("closeclick")
    })

    $.ajax({
        url: "/static/test_data4.json",
        dataType: "json",
        success: function(data){
            var rides = data["rides"]


            for (var i = 0; i < rides.length; i++) {
                var path = google.maps.geometry.encoding.decodePath(rides[i]["path"])
                var poly = new google.maps.Polyline(polyOptions)

                poly.setMap(map)
                poly.setPath(path)
            }

            // var infos = data["info"]

            // for (var i = 0; i < infos.length; i++) {
            //     var path = google.maps.geometry.encoding.decodePath(infos[i]["path"])

            //     var poly = new google.maps.Polyline(polyOptions2)

            //     poly.setMap(map)
            //     poly.setPath(path)

            //     attachWindow(map, poly, infos[i]["videos"])
            // }
        }
    })
}

function drawMarker(map, lat, lng, opacity) {
    var marker = new google.maps.Marker({
                        position: {lat: lat, lng: lng},
                        title: lat + "," + lng,
                        opacity: opacity,
                        map: map
                    })

    var infowindow = new google.maps.InfoWindow();
    google.maps.event.addListener(marker, 'click', function() {
          infowindow.setContent(lat + "," + lng);
          infowindow.open(map, marker)
    })   
}

function attachWindow(map, poly, videos) {
    var ib;
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
        var list = $("<ul/>", {"class":"listbox", "id":"listid"})

        for (var i = 0; i < videos.length; i++) {
            var video = videos[i]
            var elem = $("<li/>")
                .append($("<img/>", {"src": video["thumb"], "height":150, "width":200}))
                .append($("<h3/>").text("Amsterdam - Paris"))
                .append($("<p/>").text(video["title"]))

            list.append(elem)
        }
        parent.append(list)

        var myOptions = {
            content: parent.html(),
            position: event.latLng,
            closeBoxMargin: "4px -46px 2px 2px",
            closeBoxURL: '/static/cross.png',
            enableEventPropagation: true
        };

        ib = new InfoBox(myOptions);
        ib.open(map);

        google.maps.event.addListener(ib,'closeclick',function(){
           map.setOptions( {scrollwheel:true} ); 
        });  
    }) 

    

}

google.maps.event.addDomListener(window, 'load', initialize);