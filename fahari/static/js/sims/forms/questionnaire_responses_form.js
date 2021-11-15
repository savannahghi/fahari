document.addEventListener("DOMContentLoaded", function() {
    var $questionnaire_response_form = $("#questionnaire_response_form");

    // Configure form validation
    $questionnaire_response_form.validate({
        errorClass: "is-invalid",
        errorElement: "span",
        submitHandler: function(form) {
            form.submit();
        }
    });

    $("#btn_next").click(function() {
        $questionnaire_response_form.submit();
    });
});
