var DEFAULT_SERVER_CONNECTION_ERROR = "An error occurred when trying to connect to the server, please try again later.";
var SCALAR_VALUE = "-", LIST_VALUE = "[]", DICT_VALUE = "{}";

/**
* Given a question group and it's completion status, annotate it to indicate
* it's completion status.
*/
function annotateQuestionGroupCompletionStatus(question_group_id, is_complete) {
    var $question_group_completion_status_badge = $(`#bdg_completion_status_badge_${question_group_id}`);

    if (is_complete)
        $question_group_completion_status_badge.removeClass("badge-warning").addClass("badge-success").html("Complete");
    else
        $question_group_completion_status_badge.removeClass("badge-success").addClass("badge-warning").html("Incomplete");
}


/**
* Given a question id and error details, annotate the question to show
* the user that the answer they have provided is not valid. Also use the
* error details to show a helpful message to the user about what they
* need to change.
*/
function annotateQuestionWithInvalidAnswer(question_id, error_details) {
    $question_answer_input = $(`[data-question=${question_id}]`);
    $question_error_container = $(`#div_question_error_${question_id}`);

    $question_answer_input.removeClass("is-valid").addClass("is-invalid");
    $question_error_container.removeClass("d-none").html(`<small>${error_details}</small>`);
}


/**
* Given a question id and the applicability status of the question, annotate
* the question to indicate to the user that the answer they provided to the
* question is valid and thus has been saved successfully.
*/
function annotateQuestionWithValidAnswer(question_id, is_not_applicable) {
    $question_answer_input = $(`[data-question=${question_id}]`);
    $question_error_container = $(`#div_question_error_${question_id}`);

    $question_answer_input.removeClass("is-invalid").addClass("is-valid");
    if (is_not_applicable) {
        $question_answer_input.prop("disabled", true);
        return;
    }

    $question_answer_input.prop("disabled", false);
    $question_error_container.html("").addClass("d-none");
}


/**
* Given serialized form data, clean and format it to a form that can be used
* easily build a request payload to be sent to the server for further
* processing and for persisting.
*/
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


/**
* Given cleaned form data, build a valid request payload to be sent to the
* server. A valid request payload is a json object were question pks' form
* the keys and their values are objects containing answer and comments values.
*/
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


/**
* Called on a successful submission of question group answers. Note that in
* this context, a submission is considered successful if a status of 200
* is returned and does not imply that all answers were saved successfully.
*
* For invalid answers, this method expects that the server will still return
* a status of 200 but also include the validation error details in the
* response data.
*/
function handleDataOnSuccessQuestionGroupAnswerSubmission(data) {
    if (data["success"] != true)
        return;

    // Iterate through each valid answer and annotate each
    // question with a valid answer appropriately.
    for (var question_id in data.answers) {
        if (!data.answers.hasOwnProperty(question_id))
            continue;

        answer_data = data.answers[question_id].data;
        annotateQuestionWithValidAnswer(question_id, answer_data.is_not_applicable);
    }

    // Iterate through the validation errors and annotate each
    // question with an invalid answer appropriately.
    for (var question_id in data.errors) {
        error_details = data.errors[question_id][0];  // Only show one error at a time.
        annotateQuestionWithInvalidAnswer(question_id, error_details);
    }

    // Annotate question group completion status.
    annotateQuestionGroupCompletionStatus(data.question_group.id, data.question_group.is_complete);
}


/**
* Handle errors that occur during question group answers submission. If error
* details is null or undefined, then the error widget will be hidden,
* otherwise it will be displayed.
*/
function handleErrorOnQuestionGroupAnswerSubmission(question_group_id, error_details=null) {
    var $question_group_error_container = $(`#div_question_group_error_${question_group_id}`);

    if (error_details)
        $question_group_error_container.removeClass("d-none").html(error_details);
    else
        $question_group_error_container.html("").addClass("d-none");
}


/**
* Handle errors that occur during the submission of a questionnaire or any
* other "top level" errors that aren't suitable to shown using a question
* group's error container. If error details is null or undefined, then the
* error widget will be hidden, otherwise it will be displayed.
*/
function handleErrorOnQuestionnaireSubmission(error_details=null) {
    var $questionnaire_error_container = $("#div_questionnaire_error");

    if (error_details)
        $questionnaire_error_container.removeClass("d-none").html(error_details);
    else
        $questionnaire_error_container.html("").addClass("d-none");
}


/**
* A simple helper method that can be used to construct ana make an ajax request.
*/
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


/**
* Given a question group and it's applicability toggle element, mark it is
* applicable. This involves sending a request to the backend and once
* successful, modifying DOM elements including the given toggle element
* to indicate to the user that the given question group is indeed
* applicable and the user should thus provide answers to the question group's
* questions.
*/
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
    var complete_handler = function(xhr, status) {
        $tgl_applicability_toggle.bootstrapToggle("enable");
        $spn_spinner_question_group.addClass("d-none");

        if (status === "error")
            handleErrorOnQuestionnaireSubmission(DEFAULT_SERVER_CONNECTION_ERROR);
        else
            handleErrorOnQuestionnaireSubmission(null);
    }
    var data = JSON.stringify({
        question_group: question_group_id
    });
    var error_handler = function(request, status, error_thrown) {
        $btn_save_changes.prop("disabled", true);
        $clp_toggle_question_group.prop("disabled", true);
        $tgl_applicability_toggle.bootstrapToggle("enable");
        $tgl_applicability_toggle.bootstrapToggle("off", true);
    }
    var mark_as_applicable_url = $tgl_applicability_toggle.data("mark_as_applicable");
    var success_handler = function(data, status) {
        handleDataOnSuccessQuestionGroupAnswerSubmission(data);
        $btn_save_changes.prop("disabled", false);
        $clp_toggle_question_group.prop("disabled", false);
    }

    makeRequest(mark_as_applicable_url, data, "POST", before_send, success_handler, error_handler, complete_handler);
}



/**
* Given a question group and it's applicability toggle element, mark it is
* non-applicable. This involves sending a request to the backend and once
* successful, modifying DOM elements including the given toggle element
* to indicate to the user that the given question group is not applicable.
* This will result in the user not being able to provide answers to the
* question group's questions.
*/
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
    var complete_handler = function(xhr, status) {
        $spn_spinner_question_group.addClass("d-none");
        $tgl_applicability_toggle.bootstrapToggle("enable");

        if (status === "error") {
            handleErrorOnQuestionGroupAnswerSubmission(question_group_id, DEFAULT_SERVER_CONNECTION_ERROR);
            $tgl_applicability_toggle.bootstrapToggle("on", true);
         } else {
            handleErrorOnQuestionGroupAnswerSubmission(question_group_id, null);
         }
    }
    var data = JSON.stringify({
        question_group: question_group_id
    });
    var error_handler = function(request, status, error_thrown) {
        $btn_save_changes.prop("disabled", false);
        $clp_toggle_question_group.prop("disabled", false);
        $clp_collapse_question_group.collapse("show");
        $tgl_applicability_toggle.bootstrapToggle("on", true);
    }
    var mark_as_non_applicable_url = $tgl_applicability_toggle.data("mark_as_non_applicable");
    var success_handler = function(data, status) {
        handleDataOnSuccessQuestionGroupAnswerSubmission(data);
    }

    makeRequest(mark_as_non_applicable_url, data, "POST", before_send, success_handler, error_handler, complete_handler);
}


/**
* This is a helper function that parses a question's answer input element
* name to retrieve information such as the actual field name as expected by
* the backend, the question id and the question type. All the extracted info
* is returned as a javascript object.
*/
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
            complete: function(xhr, status) {
                $(this_button).prop("disabled", false);
                $(this_button).html("Save Changes");

                if (status === "error")
                    handleErrorOnQuestionGroupAnswerSubmission(question_group_pk, DEFAULT_SERVER_CONNECTION_ERROR);
                else
                    handleErrorOnQuestionGroupAnswerSubmission(question_group_pk, null);
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
               handleDataOnSuccessQuestionGroupAnswerSubmission(data);
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
