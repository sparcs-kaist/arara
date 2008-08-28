$(document).ready(function() {
    $("#remove_button").click(function(event) {
        $("#confirm_remove").show("slow");
        $("#acc_remove_buttons").hide("slow");
    });
    $("#dont_remove").click(function(event) {
        $("#acc_remove_buttons").show("slow");
        $("#confirm_remove").hide("slow");
    });
});
