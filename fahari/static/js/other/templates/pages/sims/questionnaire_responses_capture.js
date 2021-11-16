document.addEventListener("DOMContentLoaded", function() {
    function retrieveQuestionIdFromInputName(input_name, delimiter=":::") {
        var end_of_input_name = input_name.indexOf(delimiter);
        var field_name = input_name.substring(0, end_of_input_name);
        var question_id = input_name.substring(end_of_input_name + delimiter.length);

        return {field_name: field_name, question_id: question_id};
    }

    $("form.question_group_answers_form button.save_changes").on("click", function() {
        var question_group_pk = $(this).data("question_group");
        var question_group_form_data = $(`#question_group_form_${question_group_pk}`).serializeArray();
        var questions_answers_data = {};
        for (var index = 0; index < question_group_form_data.length; index++) {
            var form_entry = question_group_form_data[index];
            var input_name_contents = retrieveQuestionIdFromInputName(form_entry.name);

            questions_answers_data[input_name_contents.question_id] = $.extend(
                questions_answers_data[input_name_contents.question_id],
                { [input_name_contents.field_name]: form_entry.value }
            );
        }

        var this_button = this;
        var save_changes_url = $(this).data("save_changes_url");
        $.ajax({
           beforeSend: function() {
                $(this_button).prop("disabled", true);
                $(this_button).html(`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving ...`);
                return true;
            },
            complete: function() {
                $(this_button).prop("disabled", false);
                $(this_button).html("Save Changes");
            },
            contentType: "application/json; charset=UTF-8",
            data: JSON.stringify({
                question_group: question_group_pk,
                question_answers: questions_answers_data
            }),
            dataType: "json",
            error: function(request, status, error_thrown) {
//                var data = request.responseJSON;
//                console.error(data);
            },
            headers: {
                "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
            },
            method: "POST",
            success: function(data, status) {
//                console.log(data);
            },
            url: save_changes_url,
        });
    });
});
