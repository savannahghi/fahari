function showComponent($component) {
    $component.slideDown();
}


function hideComponent($component) {
    $component.slideUp();
}


document.addEventListener("DOMContentLoaded", function load() {
    $("#id_allotment_type").on("change", function() {
        $byFacilityFieldset = $("#allot_by_facility_fieldset");
        $byRegionFieldset = $("#allot_by_region_fieldset");

        // Show the appropriate fieldset based on the selected allotment type
        if (this.value === "facility") {
            showComponent($byFacilityFieldset);
            hideComponent($byRegionFieldset);
        } else if (this.value === "region") {
            showComponent($byRegionFieldset);
            hideComponent($byFacilityFieldset);
        } else if (this.value === "both") {
            showComponent($byFacilityFieldset);
            showComponent($byRegionFieldset);
        } else {
            hideComponent($byFacilityFieldset);
            hideComponent($byRegionFieldset);
        }
    }).trigger("change");  // Trigger the initial change to show the correct fieldset

    $("#id_region_type").on("change", function() {
        $countyFieldDiv = $("#div_id_counties");
        $constituencyFieldDiv = $("#div_id_constituencies");
        $subCountyFieldDiv = $("#div_id_sub_counties");
        $wardFieldDiv = $("#div_id_wards");

        if (this.value === "county") {
            showComponent($countyFieldDiv);
            hideComponent($constituencyFieldDiv);
            hideComponent($subCountyFieldDiv);
            hideComponent($wardFieldDiv);
        } else if (this.value === "constituency") {
            hideComponent($countyFieldDiv);
            showComponent($constituencyFieldDiv);
            hideComponent($subCountyFieldDiv);
            hideComponent($wardFieldDiv);
        } else if (this.value === "sub_county") {
            hideComponent($countyFieldDiv);
            hideComponent($constituencyFieldDiv);
            showComponent($subCountyFieldDiv);
            hideComponent($wardFieldDiv);
        } else if (this.value === "ward") {
            hideComponent($countyFieldDiv);
            hideComponent($constituencyFieldDiv);
            hideComponent($subCountyFieldDiv);
            showComponent($wardFieldDiv);
        } else {
            hideComponent($countyFieldDiv);
            hideComponent($constituencyFieldDiv);
            hideComponent($subCountyFieldDiv);
            hideComponent($wardFieldDiv);        }
    }).trigger("change");  // Trigger the initial change to show the correct field
})
