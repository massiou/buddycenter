// This example displays an address form, using the autocomplete feature
// of the Google Places API to help users fill in the information.
$(document).ready(function(){
$("#autocomplete").on('focus', function () {
    geolocate();
});
});


$(document).ready(function(){
var autocomplete_dict = {};
var input_autocomplete = {};
    // Create the autocomplete object, restricting the search
    // to geographical location types.
    autocomplete_array = document.getElementsByClassName('autocomplete');
    console.log(autocomplete_array);
    for(var i = 0; i < autocomplete_array.length; i++){
        autocomplete_dict["auto" + i] = document.getElementById(autocomplete_array[i].id);
        input_autocomplete["input_auto" + i] = new google.maps.places.Autocomplete(autocomplete_dict["auto" + i]);
        }
});

// [END region_geolocation]

$(document).ready(function() {
    var max_fields      = 10; //maximum input boxes allowed
    var wrapper         = $(".input_fields_wrap"); //Fields wrapper
    var add_button      = $("#add_field_button"); //Add button ID
    var autocompletes   = document.getElementsByClassName('autocomplete')
    var x = autocompletes.length - 1 ; //initlal text box count

    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        if(x < max_fields){ //max input box allowed
            x++; //text box increment
            $(wrapper).append('<div><input class="autocomplete" id="autocomplete' + x + '" placeholder="Enter address" type="text" name="address' + x + '"/><a href="#" class="remove_field"><img src="../static/images/remove.png"/></a></div>'); //add input box
            $(wrapper).append('<script>var input_auto' + x + '=new google.maps.places.Autocomplete(autocomplete' + x + ')</script>');
        }
    });

    $(wrapper).on("click",".remove_field", function(e){ //user click on remove text
        e.preventDefault(); $(this).parent('div').remove(); x--;
    })
});


$(document).ready(function(){

    $('#thedate').datepicker({
        dateFormat: 'dd-mm-yy',
        altField: '#thealtdate',
        altFormat: 'yy-mm-dd'
    });

});

