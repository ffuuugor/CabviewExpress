function initialize() {
        var mapOptions = {
          center: { lat: -34.397, lng: 150.644},
          zoom: 2
        };
        var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
        var polyOptions = {
     		strokeColor: '#FF00FF',
        	strokeOpacity: 1.0,
     		strokeWeight: 3
    	} 
    	
    	function createInfoWindow(poly,content) {
    		google.maps.event.addListener(poly, 'click', function(event) {
    			var infowindow = new google.maps.InfoWindow({
      				content: content,
      				position: event.latLng,
      				map: map
  				});
    		});
		}


		function readData() {
			var result = null;
			$.ajax({
		        async: false,
		        url: "/static/data.json",
		        dataType: "json",
		        success: function(data){
		            result = data;
		        }
	        });
	        return result
    	};
		
		var locations = readData()
        
        console.log("OLOLO")

        for (var i = 0; i < locations.length; i++) {
        	var location = locations[i]
        	poly = new google.maps.Polyline(polyOptions);   
  			var path = poly.getPath();
        	var startLatLng = new google.maps.LatLng(location.startLat, location.startLng);
        	var endLatLng = new google.maps.LatLng(location.endLat, location.endLng);

        	path.push(startLatLng)
        	path.push(endLatLng)
        	poly.setMap(map)

        	createInfoWindow(poly, location.text)
        }

      }
      google.maps.event.addDomListener(window, 'load', initialize);