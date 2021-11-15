document.addEventListener("DOMContentLoaded", function() {
    // Global vars
    window.mentor_edit_id = -1;

    // Local vars
    var $btn_save_mentor_details = $("#btn_save_mentor_details");
    var $md_capture_mentor_details_modal = $("#capture_mentor_details_modal");
    var $fm_questionnaire_response_form = $("#questionnaire_response_form");
    var $fm_mentorship_details_form = $("#mentorship_details_form");
    var $tbb_questionnaire_mentorship_team_list = $("#questionnaire-mentorship-team-list > tbody");
    var $txt_mentors = $("#id_mentors");
    var mentor_details_fields = ["name", "role", "member_org", "phone_number"];

    // Reset the form on modal close
    $md_capture_mentor_details_modal.on("hidden.bs.modal", function() {
        $fm_mentorship_details_form.trigger("reset");
        window.mentor_edit_id = -1;  // Reset the mentor id being edited
    });

    function appendMentorToMentorsTable(mentor, id) {
        var row = `<tr id="tr_mentor_details_${id}">`;
        for (var index = 0; index < mentor_details_fields.length; index++) {
            var mentor_field = mentor_details_fields[index];
            var field_value = mentor[mentor_field];
            row += `<td id="td_${mentor_field}_${id}" data-${mentor_field}="${field_value}">${field_value}</td>`;
        }
        row += `<td><a href="#" data-mentor-id="${id}"><i class="fas fa-edit"></a></td>`;
        row += "</tr>";
        $tbb_questionnaire_mentorship_team_list.append(row);
    }

    function onMentorDetailsEditClick(event) {
        event.preventDefault();
        var mentor_id = $(this).data("mentor-id");

        // Retrieve mentor data from a table row and populate the mentor detail form
        for (var index = 0; index < mentor_details_fields.length; index++) {
            var mentor_field = mentor_details_fields[index];
            var field_value = $(`#td_${mentor_field}_${mentor_id}`).data(mentor_field);
            $(`input[name=${mentor_field}`).val(field_value);
        }

        window.mentor_edit_id = mentor_id;
        $md_capture_mentor_details_modal.modal("show");
    }

    function updateMentorsTable() {
        // Reset the content of the table's body
        $tbb_questionnaire_mentorship_team_list.html("");

        var mentors = JSON.parse($txt_mentors.val());
        if (mentors && mentors.length > 0) {
            for (var index = 0; index < mentors.length; index++)
                appendMentorToMentorsTable(mentors[index], index);
        } else {
            var empty_row = `
                <tr class="odd">
                    <td valign="top" colspan="5" class="dataTables_empty">No mentors added yet</td>
                </tr>
            `;
            $tbb_questionnaire_mentorship_team_list.append(empty_row);
        }

        // Add click listeners to all the mentor entries
        $("#questionnaire-mentorship-team-list > tbody > tr > td > a").on("click", onMentorDetailsEditClick);
    }

    // Configure mentor details form validation
    $fm_mentorship_details_form.validate({
        errorClass: "is-invalid",
        errorElement: "span",
        submitHandler: function(form) {
            var form_data = $(form).serializeArray();
            var mentor_data = {};
            for (var index = 0; index < form_data.length; index++) {
                mentor_data[form_data[index].name] = form_data[index].value;
            }

            var mentors = JSON.parse($txt_mentors.val());
            mentors = (mentors)? mentors : [];
            if (window.mentor_edit_id > -1) {   // Edit an existing record
                mentors[window.mentor_edit_id] = mentor_data;
            } else {                            // Add a new record
                mentors.push(mentor_data);
            }
            $txt_mentors.val(JSON.stringify(mentors));
            updateMentorsTable();

            $md_capture_mentor_details_modal.modal("hide");
        }
    });

    updateMentorsTable();

    $btn_save_mentor_details.click(function(event) {
        $fm_mentorship_details_form.submit();
        $fm_mentorship_details_form.trigger("reset");
    });
});
