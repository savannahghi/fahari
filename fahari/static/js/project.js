(function($) {
    /* Google Analytics */
    window.dataLayer = window.dataLayer || [];

    function gtag() {
        dataLayer.push(arguments);
    }
    gtag("js", new Date());
    gtag("config", "G-WW2W29ZMTZ");
})(jQuery);


$(document).ready(function(){
    // auto-collapse open menus in responsive mode
    $(".navbar-collapse a").click(function() {
        $(".navbar-collapse").collapse("hide");
    });

    // Initialize the bootstrap select plugin
    $("select").selectpicker();
});
