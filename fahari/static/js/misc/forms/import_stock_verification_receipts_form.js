document.addEventListener("DOMContentLoaded", function load() {
    var $fst_status = $("#status_fieldset");
    var $txt_status = $("#id_status");
    $("#id_adapter").on("change", function() {
        $txt_status.val("");

        if (!this.value) {
            $fst_status.slideUp();  // Hide the status field set.
            return;
        }

        var fst_original_content = $fst_status.html();
        $fst_status.html(`
            <div class="d-flex justify-content-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
            </div>
        `);
        $fst_status.slideDown();
        $.ajax({
            url: `/api/stock_receipts_adapters/${this.value}/`,
            dataType: "json",
            error: function (_, __, error_message) {
                var status = `Error: ${error_message}`;

                $fst_status.html(fst_original_content);
                $("#id_status").val(status);
            },
            success: function (data) {
                    var status = `Google spreadsheet id : ${data["sheet_id"]}
Data sheet name       : ${data["data_sheet_name"]}
Last imported on      : ${!data["last_ingested"]? "Never" : data["last_ingested"]}
Rows imported so far  : ${data["position"]}`;

                $fst_status.html(fst_original_content);
                $("#id_status").val(status);
            },
        });
    }).trigger("change");
});
