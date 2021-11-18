var SCALAR_VALUE = "-", LIST_VALUE = "[]", DICT_VALUE = "{}";


function cleanFormData(serialized_form_data) {
    var cleaned_form_data = {};
    for (var index = 0; index < serialized_form_data.length; index++) {
        var form_entry = serialized_form_data[index];

        var cleaned_form_value = (typeof form_entry.value === "string")? form_entry.value.trim() : form_entry.value;
        if (cleaned_form_data.hasOwnProperty(form_entry.name))
            cleaned_form_data[form_entry.name].push(cleaned_form_value);
        else
            cleaned_form_data[form_entry.name] = [cleaned_form_value];
    }

    return cleaned_form_data;
}


function composeQuestionAnswersRequestPayload(cleaned_form_data) {
    var request_payload = {};
    for (var form_input_name in cleaned_form_data) {
        if (!cleaned_form_data.hasOwnProperty(form_input_name))
            continue;

        var input_name_contents = retrieveQuestionDataFromInputName(form_input_name);
        var input_value = cleaned_form_data[form_input_name];
        request_payload[input_name_contents.question_id] = $.extend(
            request_payload[input_name_contents.question_id],
            { [input_name_contents.field_name]: (input_value.length === 1)? input_value[0] : input_value }
        );
    }

    return request_payload;
}


function markQuestionGroupAsApplicable(question_group_id) {
    var $clp_toggle_question_group = $(`#clp_toggle_${question_group_id}`);
    $clp_toggle_question_group.prop("disabled", false);
}


function markQuestionGroupAsNonApplicable(question_group_id) {
    var $clp_collapse_question_group = $(`#clp_${question_group_id}`);
    var $clp_toggle_question_group = $(`#clp_toggle_${question_group_id}`);
    $clp_collapse_question_group.collapse("hide");
    $clp_toggle_question_group.prop("disabled", true);
}


function retrieveQuestionDataFromInputName(input_name, delimiter=":::", list_type_char="[]", dict_type_char="{}") {
    var end_of_field_name = input_name.indexOf(delimiter);
    var field_name = input_name.substring(0, end_of_field_name);
    var question_id_and_type = input_name.substring(end_of_field_name + delimiter.length);
    var end_of_question_id = question_id_and_type.indexOf(delimiter);
    var question_id = question_id_and_type.substring(0, end_of_question_id);
    var question_type = question_id_and_type.substring(end_of_question_id + delimiter.length)

    return {field_name: field_name, question_id: question_id, question_type: question_type};
}


document.addEventListener("DOMContentLoaded", function() {
    $(".applicability_toggle").on("change", function() {
        var question_group_id = $(this).data("question_group");
        var question_group_applicability = $(this).prop("checked");

        if (!question_group_applicability)
            markQuestionGroupAsNonApplicable(question_group_id);
        else
            markQuestionGroupAsApplicable(question_group_id)
    });

    $("form.question_group_answers_form button.save_changes").on("click", function() {
        var question_group_pk = $(this).data("question_group");
        var question_group_form_data = $(`#question_group_form_${question_group_pk}`).serializeArray();
        var cleaned_form_data = cleanFormData(question_group_form_data);
        var questions_answers_data = composeQuestionAnswersRequestPayload(cleaned_form_data);

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
