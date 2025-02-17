//========================================================================================
//    HTML5 responsive Webpage to display Volker's sailing trips utilising:
//      - Google Maps API v3 to display the map
//      - MySQL DBs to store and retrieve the trip data
//      - Bootstrap ver 5.0.1 framework
//
//	  This Sailinglog.js contains all common JavaScripts utilized by this webpage
//
//    (c) Kaiserware, Volker Petersen, 2011-2021
//========================================================================================

// global variables
let data_table;
let num_trips = -1;

jQuery(document).ready(function () {
	updateMenuHighlight();
});

//-----------------------------------------------------------------------------------------
// JQuery function to enlarge an image upon the "mouseover" event
//     function is disabled on phones with the absence of the enlarge 
//     class in the image tag in the index.html code generator
//-----------------------------------------------------------------------------------------
this.imageEnlarge = function(){
	$("img.enlarge").mouseover(function () {
		//console.log("image enlarge function");
		$("body").append("<div id='largeImageBox' class='float-picture'><img src='"+ this.src +"' width='600' alt='Image preview' /><p id='enlarged' class='bodytextitalic' align='center'>"+ this.alt +"</p></div>");
		$("#Layer20").fadeIn("slow");
		var offset = window.scrollY
		//console.log("offset:"+offset)
		$(".float-picture").offset({ top: offset+230 })
	});
	$("img.enlarge").mouseout(function(){
		$(".float-picture").remove();
	});
};



//-----------------------------------------------------------------------------------------
// function to swap an element in a class definition
//-----------------------------------------------------------------------------------------
function swapClassElement(element, class_1, class_2) {
	var order = "";
	if ( $( element ).attr("class") == class_1 ) {
		$( element ).removeClass(class_1).addClass(class_2);
		//alert("set class_1 to class_2 attribute");
		order = "desc";  // sort in descending order
	} else {
		$( element ).removeClass(class_2).addClass(class_1);
		//alert("set class_2 to class_1 attribute");
		order = "asc";  // sort in ascending order
	}
	return order;
}

function sort_by_name(a, b) {
	return a.innerHTML.toLowerCase().localeCompare(b.innerHTML.toLowerCase());
}

//-----------------------------------------------------------------------------------------
// function to change out special characters
//-----------------------------------------------------------------------------------------
function special_char(value) {
	value = value.replace(/ä/g, "&auml;");
	value = value.replace(/ö/g, "&ouml;");
	value = value.replace(/ü/g, "&uuml;");
	return value;
}

//-----------------------------------------------------------------------------------------
// function to enhance the html code returned by Javascript function 'parse_trip_table()'.
// We add imageEnlarge property, fix the container sizes and make the
// DataTable sortable or not based on the devise / screen mode.
// The variable isMobile is set in header.html
//-----------------------------------------------------------------------------------------
function enhance_toern_table_code(isMobile) {
	imageEnlarge();

	if (isMobile) {
		data_table = $("#toern_table").DataTable({
			searching: true,
			paging: false,
			info: false,
			ordering: false
		});
	} else {
		data_table = $("#toern_table").DataTable({
			searching: true,
			paging: false,
			info: false,
			ordering: true
		});
	}

}


//-----------------------------------------------------------------------------------------
// Function to format a float number to 1 decimal with thousand comma separators
//-----------------------------------------------------------------------------------------
function numberWithCommas(value, decimals) {
	try {
		value = value.toFixed(decimals);
		return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
	} catch {
		value = 0;
		value = value.toFixed(decimals);
		return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
	}

}

//-----------------------------------------------------------------------------------------
// Function to test is str variable is empty (""=False) or not (=True)
//-----------------------------------------------------------------------------------------
function is_string_empty(str) {
	if (str && str.trim().length) {
		return true;
	} else {
		return false;
	}
}

//-----------------------------------------------------------------------------------------
// Javascript function to highlight the currently active Menu option
//-----------------------------------------------------------------------------------------
function updateMenuHighlight() {
	var path = window.location.pathname;
	var menuitem;
	var href;
	if (path.length < 1) {
		path = '/';
	}

	jQuery("#MainMenu a").each(function () {
		href = $(this).attr('href');
		menuitem = $(this).closest('li');
		if(menuitem.hasClass('active')) {
			menuitem.removeClass('active'); // remove active class
		}
		//console.log("path="+path+"  href="+href+"  search="+(path.indexOf(href) != -1).toString()+path.indexOf(href));
		if (path.indexOf(href) != -1 && href.length>1 || path==href) {
		  //console.log("menuitem="+menuitem.html());
		  menuitem.addClass('active'); // add active class to current menu item that corresponds to the link address
		  menuitem.parent().parent('li').addClass('active');  // add active class to the parent <li> for submenu
		}
	}); // end of Menu focus jQuery function
}

//-----------------------------------------------------------------------------------------
// function to format number to string
//-----------------------------------------------------------------------------------------
function number_format (number, decimals, dec_point, thousands_sep) {
  // http://kevin.vanzonneveld.net
  // +   original by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
  // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
  // +     bugfix by: Michael White (http://getsprink.com)
  // +     bugfix by: Benjamin Lupton
  // +     bugfix by: Allan Jensen (http://www.winternet.no)
  // +    revised by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
  // +     bugfix by: Howard Yeend
  // +    revised by: Luke Smith (http://lucassmith.name)
  // +     bugfix by: Diogo Resende
  // +     bugfix by: Rival
  // +      input by: Kheang Hok Chin (http://www.distantia.ca/)
  // +   improved by: davook
  // +   improved by: Brett Zamir (http://brett-zamir.me)
  // +      input by: Jay Klehr
  // +   improved by: Brett Zamir (http://brett-zamir.me)
  // +      input by: Amir Habibi (http://www.residence-mixte.com/)
  // +     bugfix by: Brett Zamir (http://brett-zamir.me)
  // +   improved by: Theriault
  // +      input by: Amirouche
  // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
  // *     example 1: number_format(1234.56);
  // *     returns 1: '1,235'
  // *     example 2: number_format(1234.56, 2, ',', ' ');
  // *     returns 2: '1 234,56'
  // *     example 3: number_format(1234.5678, 2, '.', '');
  // *     returns 3: '1234.57'
  // *     example 4: number_format(67, 2, ',', '.');
  // *     returns 4: '67,00'
  // *     example 5: number_format(1000);
  // *     returns 5: '1,000'
  // *     example 6: number_format(67.311, 2);
  // *     returns 6: '67.31'
  // *     example 7: number_format(1000.55, 1);
  // *     returns 7: '1,000.6'
  // *     example 8: number_format(67000, 5, ',', '.');
  // *     returns 8: '67.000,00000'
  // *     example 9: number_format(0.9, 0);
  // *     returns 9: '1'
  // *    example 10: number_format('1.20', 2);
  // *    returns 10: '1.20'
  // *    example 11: number_format('1.20', 4);
  // *    returns 11: '1.2000'
  // *    example 12: number_format('1.2000', 3);
  // *    returns 12: '1.200'
  // *    example 13: number_format('1 000,50', 2, '.', ' ');
  // *    returns 13: '100 050.00'
  // Strip all characters but numerical ones.
  number = (number + '').replace(/[^0-9+\-Ee.]/g, '');
  var n = !isFinite(+number) ? 0 : +number,
	prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
	sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
	dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
	s = '',
	toFixedFix = function (n, prec) {
	  var k = Math.pow(10, prec);
	  return '' + Math.round(n * k) / k;
	};
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  if (s[0].length > 3) {
	s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '').length < prec) {
	s[1] = s[1] || '';
	s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}
