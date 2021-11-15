document.addEventListener("DOMContentLoaded", function() {
    // Set up progress bar
    var $div_progress = $("#div_progress").hide();
    var $div_progress_bar = $("#div_progress_bar");

    // Set up import button
    var $btn_ingest_data = $("#btn_ingest_data");
    $btn_ingest_data.disable = function() {
        $(this).prop("disabled", true);
    };
    $btn_ingest_data.startLoading = function(text) {
        $(this).prop("disabled", true);
        $(this).html(`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${text}`);
    };
    $btn_ingest_data.stopLoading = function() {
        $(this).prop("disabled", false);
        $(this).html("Import");
    };

    // Set up status textarea
    var $txt_status = $("#id_status");
    $txt_status.addDivider = function() {
        var columns = parseInt($(this).attr("cols"));
        var divider = "-";
        for (var index = 1; index < columns; index++)
            divider += "-"
        this.appendContent("\n\n" + divider + "\n");
    };
    $txt_status.appendContent = function(new_content) {
        var $_txt_status = $("#id_status");
        $_txt_status.val($_txt_status.val() + new_content);
    };
    $txt_status.scrollToBottom = function() {
        var $_txt_status = $("#id_status");
        $_txt_status.animate({
            scrollTop: $_txt_status.prop("scrollHeight") - $_txt_status.height()
        }, 1000);
    };

    // Set up web socket
    function startIngestSocket() {
        $btn_ingest_data.startLoading("Connecting...");
        var protocol = (window.location.protocol === "https:")? "wss://" : "ws://";
        var socket = new WebSocket(protocol + window.location.host + "/ws/misc/stock_receipts_verification_ingest/");
        socket.addEventListener("open", function() {
            $btn_ingest_data.stopLoading();
        });
        socket.addEventListener("message", function(e) {
            var data = JSON.parse(e.data);
            switch (data.type) {
                case "error":
                    handleErrorMessage(data.data.row_index, data.data.error_messages);
                    break;
                case "progress":
                    handleProgressMessage(data.data.current, data.data.total, data.data.percentage);
                    break;
                case "success":
                    handleSuccessMessage(data.data.ingested_rows);
                    break;
                default:
                    console.error("Invalid data received: ", data);
            }
        });
        socket.addEventListener("close",  function(e) {
            $btn_ingest_data.stopLoading();
        });

        return socket;
    }
    var ingest_socket = startIngestSocket();

    // Handlers
    function handleErrorMessage(row_index, error_messages) {
        $div_progress.slideUp();
        $btn_ingest_data.stopLoading();

        $txt_status.addDivider();
        for (var index = 0; index < error_messages.length; index++)
            $txt_status.appendContent(error_messages[index] + "\n");
        $txt_status.scrollToBottom();
    }

    function handleProgressMessage(current, total, percentage) {
        $div_progress_bar.css("width", Math.min(Math.round(percentage), 100) + "%");
    }

    function handleSuccessMessage(ingested_rows) {
        $div_progress.slideUp();
        $btn_ingest_data.stopLoading();

        $txt_status.addDivider();
        if (ingested_rows === 0)
            $txt_status.appendContent("Nothing to import, everything up to date.\n");
        else
            $txt_status.appendContent("Successfully imported " + ingested_rows + " rows.\n");
        $txt_status.scrollToBottom();
    }

    $fm_import_stock_verification_receipts_form = $("#import_stock_verification_receipts_form");

    // Handle import click
    $btn_ingest_data.click(function(event) {
         $fm_import_stock_verification_receipts_form.validate({
            errorClass: "is-invalid",
            errorElement: "span"
         });
         if (!$fm_import_stock_verification_receipts_form.valid()) {
            return;
         }

         // Make sure we are connected to the server before proceeding
         if (ingest_socket.readyState >= 2)
            ingest_socket = startIngestSocket();

         // Compose request data
         var request_data = {};
         var form_values = $("#import_stock_verification_receipts_form").serializeArray();
         for (var index = 0; index < form_values.length; ++index) {
              var entry = form_values[index];
              request_data[entry.name] = entry.value;
         }
         request_data = JSON.stringify(request_data);

         // Prepare the DOM
         handleProgressMessage(0, 100, 0);  // reset the progress bar
         $btn_ingest_data.startLoading("Importing...");
         $div_progress.slideDown();

         // Send the data
         ingest_socket.send(request_data);
    });
});
