var SCALAR_VALUE = "-", LIST_VALUE = "[]", DICT_VALUE = "{}";


function annotateQuestionAnswerInput(question_id, is_valid, not_applicable=False) {
    $question_answer_input = $(`[data-question=${question_id}]`);
    if (not_applicable) {
        $question_answer_input.addClass();
        $question_answer_input.prop("disabled", true);
        return;
    }

    $question_answer_input.prop("disabled", false);
    if (is_valid)
        $question_answer_input.addClass("is-valid");
    else
        $question_answer_input.addClass("is-invalid");
}


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


function makeRequest(url, data, method = "POST", before_send = () => true, success_handler = () => undefined, error_handler = () => undefined, complete_handler = () => undefined) {
    $.ajax({
        beforeSend: before_send,
        complete: complete_handler,
        contentType: "application/json; charset=UTF-8",
        data: data,
        dataType: "json",
        error: error_handler,
        headers: {
            "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
        },
        method: method,
        success: success_handler,
        url: url,
    });
}


function markQuestionGroupAsApplicable(question_group_id, $tgl_applicability_toggle) {
    var $btn_save_changes = $(`#btn_save_changes_${question_group_id}`);
    var $clp_collapse_question_group = $(`#clp_${question_group_id}`);
    var $clp_toggle_question_group = $(`#clp_toggle_${question_group_id}`);
    var $spn_spinner_question_group = $(`#spn_spinner_question_group_${question_group_id}`);

    var before_send = function() {
        $tgl_applicability_toggle.bootstrapToggle("disable");
        $spn_spinner_question_group.removeClass("d-none");
        return true;
    }
    var complete_handler = function() {
        $tgl_applicability_toggle.bootstrapToggle("enable");
        $spn_spinner_question_group.addClass("d-none");
    }
    var data = JSON.stringify({
        question_group: question_group_id
    });
    var error_handler = function(request, status, error_thrown) {
        $btn_save_changes.prop("disabled", true);
        $clp_toggle_question_group.prop("disabled", true);
        $tgl_applicability_toggle.bootstrapToggle("off", true);
    }
    var mark_as_applicable_url = $tgl_applicability_toggle.data("mark_as_applicable");
    var success_handler = function(data, status) {
        if (data["success"] != true)
            return;

        for (var answer_id in data.answers) {
            if (!data.answers.hasOwnProperty(answer_id))
                continue;

            answer_data = data.answers[answer_id].data;
            annotateQuestionAnswerInput(answer_data.question, answer_data.is_valid, answer_data.is_not_applicable);
        }

        $btn_save_changes.prop("disabled", false);
        $clp_toggle_question_group.prop("disabled", false);
    }

    makeRequest(mark_as_applicable_url, data, "POST", before_send, success_handler, error_handler, complete_handler);
}


function markQuestionGroupAsNonApplicable(question_group_id, $tgl_applicability_toggle) {
    var $btn_save_changes = $(`#btn_save_changes_${question_group_id}`);
    var $clp_collapse_question_group = $(`#clp_${question_group_id}`);
    var $clp_toggle_question_group = $(`#clp_toggle_${question_group_id}`);
    var $spn_spinner_question_group = $(`#spn_spinner_question_group_${question_group_id}`);

    var before_send = function() {
        $btn_save_changes.prop("disabled", true);
        $clp_collapse_question_group.collapse("hide");
        $clp_toggle_question_group.prop("disabled", true);
        $spn_spinner_question_group.removeClass("d-none");
        $tgl_applicability_toggle.bootstrapToggle("disable");
        return true;
    }
    var complete_handler = function() {
        $spn_spinner_question_group.addClass("d-none");
        $tgl_applicability_toggle.bootstrapToggle("enable");
    }
    var data = JSON.stringify({
        question_group: question_group_id
    });
    var error_handler = function(request, status, error_thrown) {
        $btn_save_changes.prop("disabled", false);
        $clp_toggle_question_group.prop("disabled", false);
        $tgl_applicability_toggle.bootstrapToggle("on", true);

        var data = request.responseJSON;
        console.error(data);
    }
    var mark_as_non_applicable_url = $tgl_applicability_toggle.data("mark_as_non_applicable");
    var success_handler = function(data, status) {
        if (data["success"] != true)
            return;

        for (var answer_id in data.answers) {
            if (!data.answers.hasOwnProperty(answer_id))
                continue;

            answer_data = data.answers[answer_id].data;
            annotateQuestionAnswerInput(answer_data.question, answer_data.is_valid, answer_data.is_not_applicable);
        }
    }

    makeRequest(mark_as_non_applicable_url, data, "POST", before_send, success_handler, error_handler, complete_handler);
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
    var $btn_submit = $("#btn_submit");
    var $btn_submit_confirm = $("#btn_submit_confirm");
    var $mdl_confirm_questionnaire_responses_submission = $("#mdl_confirm_questionnaire_responses_submission");

    $(".applicability_toggle").on("change", function() {
        var question_group_id = $(this).data("question_group");
        var question_group_applicability = $(this).prop("checked");
        var $tgl_applicability_toggle = $(this);

        if (!question_group_applicability)
            markQuestionGroupAsNonApplicable(question_group_id, $tgl_applicability_toggle);
        else
            markQuestionGroupAsApplicable(question_group_id, $tgl_applicability_toggle);
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
                if (data["success"] != true)
                    return;

                for (var answer_id in data.answers) {
                    if (!data.answers.hasOwnProperty(answer_id))
                        continue;

                    answer_data = data.answers[answer_id].data;
//                    annotateQuestionAnswerInput(answer_data.question, answer_data.is_valid, answer_data.is_not_applicable);
                }
            },
            url: save_changes_url,
        });
    });

    $btn_submit.click(function() {
        $.ajax({
            beforeSend: function() {
                $btn_submit.prop("disabled", true);
                $btn_submit.html(`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing ...`);
                return true;
            },
            complete: function() {
                $btn_submit.prop("disabled", false);
                $btn_submit.html("Submit");
            },
            error: function() {

            },
            method: "GET",
            success: function(data, success) {
                $mdl_confirm_questionnaire_responses_submission.modal("show");
                var remaining = data["questions_count"] - data["answered_question_count"];
                var message = "";
                if (remaining === 0)
                    message = "You are about to submit this questionnaire, once you do, you will not be able to edit it. Are you sure you want to proceed?"
                else
                    message = "You have " + remaining + " answered questions, if you proceed, they will be marked as non-applicable. Note that this is a non-reversible operation and once you submit, you can not edit the questionnaire. Are you sure you want to proceed?";
                $mdl_confirm_questionnaire_responses_submission.find("#p_submission_content").html(message);
            },
            url: $btn_submit.data("questionnaire_responses_stats_url")
        });
    });

    $btn_submit_confirm.click(function() {
        $("#fm_submit_form").submit();
    })
});
