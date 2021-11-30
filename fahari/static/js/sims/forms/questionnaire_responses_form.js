jQuery.validator.addMethod("at_least_1_mentor", function(value, element){
    var as_json = JSON.parse(value);
    if (!jQuery.isArray(as_json) || as_json.length === 0)
        return false;

    return true;
});


document.addEventListener("DOMContentLoaded", function() {
    var $questionnaire_response_form = $("#questionnaire_response_form");

    // Configure form validation
    $questionnaire_response_form.validate({
        errorClass: "is-invalid",
        errorElement: "div",
        errorPlacement: function(error, element) {
            error.addClass('invalid-feedback');
            element.closest('.form-group').append(error);
        },
        highlight: function(element, error_class, valid_class) {
            $(element).addClass(error_class).removeClass(valid_class);
        },
        ignore: ":not([name='mentors']):hidden",
        messages: {
            mentors: { at_least_1_mentor: "You must provide at least on mentor before you can proceed." }
        },
        rules: {
            mentors: { at_least_1_mentor: true }
        },
        showErrors: function(error_map, error_list) {
            if (error_map.hasOwnProperty("mentors")) {
                $("div.alert.alert-danger").removeClass("d-none").html(error_map["mentors"]);
            } else {
                $("div.alert.alert-danger").addClass("d-none");
            }

            this.defaultShowErrors();
        },
        submitHandler: function(form) {
            form.submit();
        },
        unhighlight: function(element, error_class, valid_class) {
            $(element).removeClass(error_class).addClass(valid_class);
        }
    });

    $("#btn_next").click(function() {
        $questionnaire_response_form.submit();
    });
});
