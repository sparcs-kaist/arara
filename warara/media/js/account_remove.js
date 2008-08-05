$(document).ready(function() {
    $("#remove_button").click(function(event) {
        $("#confirm_remove").slideDown(1000);
        $("#remove_button").slideUp(1000);
    });
    $("#dont_remove").click(function(event) {
        $("#remove_button").slideDown(1000);
        $("#confirm_remove").slideUp(1000);
    });
});
