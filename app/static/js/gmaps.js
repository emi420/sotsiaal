/*
 * WikiMapa
 * Copyright (C) 2007 Emilio Mariscal - Proyecto83.com
 * 
 * == BEGIN LICENSE ==
 * 
 * Licensed under the terms of any of the following licenses at your
 * choice:
 * 
 *  - GNU General Public License Version 2 or later (the "GPL")
 *    http://www.gnu.org/licenses/gpl.html
 * 
 *  - GNU Lesser General Public License Version 2.1 or later (the "LGPL")
 *    http://www.gnu.org/licenses/lgpl.html
 * 
 * == END LICENSE ==
 * 
 * 	File Name  / description( nombre del archivo / descripción):
 *
 * 	gmap.js
 *
 * 	Main file ( archivo principal )
 * 
 * File Authors ( autor del archivo ):
 * 		Emilio Mariscal ( emi420@gmail.com )
 */

	var map; // mapa
	var iconBlue = new GIcon();  // icono azul 
	var geocoder = '' ; // direcciones
	
    iconBlue.image = 'http://labs.google.com/ridefinder/images/mm_20_blue.png';
    iconBlue.shadow = 'http://labs.google.com/ridefinder/images/mm_20_shadow.png';
    iconBlue.iconSize = new GSize(12, 20);
    iconBlue.shadowSize = new GSize(22, 20);
    iconBlue.iconAnchor = new GPoint(6, 20);
    iconBlue.infoWindowAnchor = new GPoint(5, 1);
	
    function load() {
      if (GBrowserIsCompatible()) {
	  
		// Inicializa el mapa
        map = new google.maps.Map2(document.getElementById("map"));
		center = new GLatLng(-34.603753,-58.381605)
        map.setCenter(center, 4); // Argentina
		map.setUIToDefault();
		var x= map.getMapTypes(); 
		map.setMapType(x[0]); 
		map.enableScrollWheelZoom();
		map.enableRotation();
		geocoder = new GClientGeocoder();	
		marker = new GMarker(center, {draggable: true}) ;

		GEvent.addListener(marker, 'dragend', function() {
			document.getElementById('map_latlng').value = marker.getPoint().lat() + ',' + marker.getPoint().lng() ;
			document.getElementById('map_zoom').value = map.getZoom() ;
			//document.getElementById('map_type').value = map.getCurrentMapType() ;
		});
		
		GEvent.addListener(map, 'moveend', function() {
			document.getElementById('map_latlng').value = marker.getPoint().lat() + ',' + marker.getPoint().lng() ;
			document.getElementById('map_zoom').value = map.getZoom() ;
			//document.getElementById('map_type').value = map.getCurrentMapType() ;
		});
		
		   GEvent.addListener(map, "maptypechanged", function() { 
		   // getMapTypes()	GMapType[]	Returns the array of map types registered with this map.
			var myMapType = map.getCurrentMapType(); 
			if (myMapType == G_SATELLITE_TYPE) { 
			  document.myForm.mapType.value = "satellite"; 
			} 
			if (myMapType == G_MAP_TYPE) { 
			  document.myForm.mapType.value = "map"; 
			} 
			if (myMapType == G_HYBRID_TYPE) { 
			  document.myForm.mapType.value = "hybrid"; 
			} 
		  }); 
		
		map.addOverlay(marker);
	  }
	}
	
	function searchAddress(address) {
		map.clearOverlays() ;
		if (geocoder) {
			geocoder.getLatLng(
			  address,
			  function(point) {
				if (!point) {
				  alert("No se encuentra la direccion:" + address);
				} else {
				  map.setCenter(point, 13);
				  var marker = new GMarker(point, {draggable: true});
				  document.getElementById('map_latlng').value = point.lat() + ',' + point.lng() ;
				  document.getElementById('map_zoom').value = map.getZoom() ;

				  GEvent.addListener(marker, 'dragend', function() {
					document.getElementById('map_latlng').value = marker.getPoint().lat() + ',' + marker.getPoint().lng() ;
					document.getElementById('map_zoom').value = map.getZoom() ;
				  });

				  map.addOverlay(marker);
				  document.getElementById('map_latlng').value = marker.getPoint().lat() + ',' + marker.getPoint().lng() ;
				  document.getElementById('map_zoom').value = map.getZoom() ;
				  // marker.openInfoWindowHtml(address);
				  				  
				}
			  }
			);
		}
		return 0 ;
	}
		
			
	/*
	  * checkEnter
	  * By Jennifer Madden
	  * http://jennifermadden.com/javascript/stringEnterKeyDetector.html
	 */ 
	function checkEnter(e, action)
	{
		var characterCode
	
		if( e && e.which )
		{
			e = e ;
			characterCode = e.which ;
		} else {
			e = event ;
			characterCode = e.keyCode ;
		}
	
		if(characterCode == 13) {
			switch ( action ) {
				default: searchAddress(document.getElementById('t_map_address').value) ;
			}
			return false ;
		} else {
			return true ;
		}
	}
	
    