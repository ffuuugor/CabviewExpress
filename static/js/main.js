var rides = {};

var mapOptions = {
    center: { lat: 50.912262, lng: 8.512218},
    scrollwheel: true,
    zoom: 6,
    disableDefaultUI: true,
    mapTypeControlOptions: {
        mapTypeIds: ['styled_map']
    }
}

var visiblePolyOptions = {
    strokeColor: '#0a0175',
    strokeOpacity: 0.2,
    strokeWeight: 6
}

var redPolyOptions = {
    strokeColor: '#e87306',
    strokeOpacity: 1,
    strokeWeight: 6,
    zIndex: 100
}

var invisiblePolyOptions = {
    strokeColor: '#0a0175',
    strokeOpacity: 0,
    strokeWeight: 6,
    zIndex: 2
}

Number.prototype.toHHMMSS = function () {
    var sec_num = parseInt(this, 10); // don't forget the second param
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    var time    = hours+':'+minutes+':'+seconds;
    return time;
}

function initialize() {

    $("#close").click(function() {
        $('#vidlist').animate(
            {
                right:"-35%"
            },
            {
                complete:function() {$("#open").show();$("#close").hide()}
            }
        );
    })

    $("#open").click(function() {
        $('#vidlist').animate({right:0});
        $("#close").show()
        $("#open").hide()
    })

    $("#info").click(function() {
        console.log("ololo")
        $("#contactsLayer").show()
    })

    $("#cross").click(function() {
        $("#contactsLayer").hide()
    })

    var styledMapType = new google.maps.StyledMapType(map_style);
    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
    map.mapTypes.set('styled_map', styledMapType);
    map.setMapTypeId('styled_map');

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
        url: "/static/final_rides.json",
        dataType: "json",
        success: function(data){

            for (var i = 0; i < data.length; i++) {
                var ride = data[i]

                var path = google.maps.geometry.encoding.decodePath(ride["path"])
                var poly = new google.maps.Polyline(visiblePolyOptions)

                poly.setMap(map)
                poly.setPath(path)

                rides[ride.id] = ride;

            }
        }
    })

    $.ajax({
        url: "/static/final_segments.json",
        dataType: "json",
        success: function(data){
            for (var i = 0; i < data.length; i++) {
                var segment = data[i]

                var path = google.maps.geometry.encoding.decodePath(segment["path"])
                var poly = new google.maps.Polyline(invisiblePolyOptions)

                poly.setMap(map)
                poly.setPath(path)

                attachWindow(map, poly, segment["ride_ids"])
            }
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

function attachWindow(map, poly, ride_ids) {
    var ib;
    google.maps.event.addListener(poly, 'click', function(event) {

        $("#listid").empty()


        for (var i = 0; i < ride_ids.length; i++) {
            var video = rides[ride_ids[i]]["video"]
            var from_city = rides[ride_ids[i]]["from"]
            var to_city = rides[ride_ids[i]]["to"]

            var elem = $("<a/>", {"href": video["url"], "target":"_blank"}).append(
                $("<li/>")
                    .append(
                        $("<div/>", {"class": "image"}).append(
                            $("<img/>", {"src": video["thumb"], "height":150, "width":200})
                        ).append(
                            $("<div/>", {"class": "description"}).append(
                                $("<p/>", {"class": "description_content"}).text(video["duration"].toHHMMSS())
                            )
                        )
                    )
                    .append($("<h3/>").text(`${from_city.name} - ${to_city.name}`))
                    .append($("<p/>").text(video["title"]))
                )


            attachFullRoute(map, elem, rides[ride_ids[i]]["path"])


            $("#listid").append(elem)
        }

        $('#vidlist').animate({right:0});
        if ($("#open").is(":visible")) {
            $("#close").show()
            $("#open").hide()    
        }

    }) 
}

function attachFullRoute(map, elem, path) {
    var path = google.maps.geometry.encoding.decodePath(path)
    var poly = new google.maps.Polyline(redPolyOptions)
    poly.setPath(path)

    elem.mouseenter(function(){
        poly.setMap(map)
        
    })

    elem.mouseleave(function(){
        poly.setMap(null)
    })    
}

google.maps.event.addDomListener(window, 'load', initialize);