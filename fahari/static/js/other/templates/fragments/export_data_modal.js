document.addEventListener("DOMContentLoaded", function() {
    var $dump_fields_selection_tree = $("#div_dump_fields_selection_tree").jstree({
        "core": {
            "data": {
                "url": window.available_fields_url,
            },
            "themes": {
                "name": "default",
                "responsive": true
            },
        },
        "checkbox" : {
            "keep_selected_style" : false
        },
        "plugins": ["checkbox"],
    });

    var $filterset_form = $("#fm_filter_form");
    var $div_filter_form_content = $("#div_form_content");
    var $div_filter_form_loading_indicator = $("#div_loading_indicator");
    // Load the filterset form
    $.ajax({
        beforeSend: function() {
            $div_filter_form_loading_indicator.html(`
                <div class="d-flex justify-content-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="sr-only">Loading...</span>
                    </div>
                </div>
            `);
            return true;
        },
        dataType: "html",
        error: function() {
            $div_filter_form_loading_indicator.html("");
            $div_filter_form_content.html("Error loading filter form, please try again later.").addClass("text-center ");
        },
        success: function(data) {
            $div_filter_form_loading_indicator.html("");
            $div_filter_form_content.html(data);
        },
        url: window.get_filter_form_url
    });

    var $btn_dump_data = $("#btn_dump_data");
    $btn_dump_data.startLoading = function(text) {
        $(this).prop("disabled", true);
        $(this).html(`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${text}`);
    };
    $btn_dump_data.stopLoading = function() {
        $(this).prop("disabled", false);
        $(this).html("Export");
    }
    $btn_dump_data.click(function(event) {
        var dump_fields_selection = $dump_fields_selection_tree.jstree("get_selected");
        if (dump_fields_selection.length === 0) {
            alert("You must select the fields to be exported.");
            event.preventDefault();
            return;
        }

        // Build the request by adding the selected dump fields to the filter fields
        var filters = $filterset_form.serializeArray();
        for (var index = 0; index < dump_fields_selection.length; ++index) {
            filters.push({name: "dump_fields", value: dump_fields_selection[index]});
        }
        $.ajax({
            beforeSend: function() {
                $btn_dump_data.startLoading("Processing...");
                return true;
            },
            complete: function() {
                $btn_dump_data.stopLoading();
            },
            contentType: "application/json; charset=UTF-8",
            data: filters,
            url: window.dump_data_url,
        });
    });
});
