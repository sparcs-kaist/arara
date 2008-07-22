
$(document).ready(function(){
    var user_popup = $("#user_popup");
    user_popup.hide();
    user_popup.addClass("absolute");

    $("#user_popup li").hover(
    function(event) {
        $(this).addClass("user_popup_menu_hover");
    },
    function(event) {
        $(this).removeClass("user_popup_menu_hover");
    });

    $(".username").click(function(event) {
        var username = $(this).text();
        $("#user_popup #user_popup_username").text("User: " + username);

        $("#user_popup").css("top", $(this).offset()["top"] + $(this).height())
        $("#user_popup").css("left", $(this).offset()["left"])

        $("#user_popup").show("fast");
        event.stopPropagation( ) 
    });

    $("#user_popup_send_message").click(function(event) {
        alert("hello, world!");
    });

    $("html").click(function(event) {
        $("#user_popup").hide("fast");
    });
});
