$(document).ready(function(){
    $(".delete_user").click(function(event) {
        $("#blacklist_delete_form #username").attr("value", this.name);
        $("#blacklist_delete_form").submit();
    });
    $("#bl_update_submit").click(function(event) {
        event.preventDefault();
        $("#bl_mypage_chart #bl_submit_chooser").attr("value", "update");
        $("#bl_mypage_chart").submit();
    });
    $("#bl_delete_submit").click(function(event) {
        event.preventDefault();
        $("#bl_mypage_chart #bl_submit_chooser").attr("value", "delete");
        $("#bl_mypage_chart").submit();
    });
    /*if done is chosen .attr("value", "update")
 * if delete is hosne, .attr("value", "delete") */
});
