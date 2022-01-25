/**
* Given an element, return the element's label text.
*
* This function only works if the given element has an `id` attribute and the
* element's label has a `for` attribute whose value is the given element's
* `id`. Otherwise, an empty string will be returned.
*/
function getElementLabelText($element) {
    var element_id = $($element).attr("id");
    return $(`label[for='${element_id}']`).text().trim();
}

(function($) {
    /* Google Analytics */
    window.dataLayer = window.dataLayer || [];

    function gtag() {
        dataLayer.push(arguments);
    }
    gtag("js", new Date());
    gtag("config", "G-WW2W29ZMTZ");

    // auto-collapse open menus in responsive mode
    $(".navbar-collapse a").click(function() {
        $(".navbar-collapse").collapse("hide");
    });

    // Initialize the select2 plugin
    $("select").each(function () {
        $(this).select2({
            allowClear: typeof $(this).data("allow-clear") !== "undefined" ? Boolean($(this).data("allow-clear")) : Boolean($(this).attr("multiple")),
            closeOnSelect: !$(this).attr("multiple"),
            placeholder: typeof $(this).data("placeholder") !== "undefined" ? $(this).data("placeholder") : {"id": `select2__placeholder__id__{$(this).attr('id')}`, "placeholder": `Select ${getElementLabelText(this)}`},
            theme: "bootstrap4",
            width: $(this).data("width") ? $(this).data("width") : $(this).hasClass("w-100") ? "100%" : "resolve",
        });
    });

    // Initialize the date picker plugin
    $(".datepicker").datepicker();
})(jQuery);
