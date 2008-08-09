
$(document).ready(function(){
    var user_popup = $("#user_popup");
    user_popup.addClass("absolute");
    var message_popup = $("#message_popup");
    message_popup.addClass("absolute");

    $("#user_popup li").hover(
    function(event) {
        $(this).addClass("user_popup_menu_hover");
    },
    function(event) {
        $(this).removeClass("user_popup_menu_hover");
    });

    $(".username").hover(
    function(event) {
        $(this).addClass("username_highlight");
    },
    function(event) {
        $(this).removeClass("username_highlight");
    });

    var username;
    $(".username").click(function(event) {
        username = $(this).text();
        $("#user_popup #user_popup_username").text("User: " + username);

        $("#user_popup").css("top", $(this).offset()["top"] + $(this).height())
        $("#user_popup").css("left", $(this).offset()["left"])

        $("#user_popup").show("fast");
        event.stopPropagation(); 
    });

    $("#user_popup_send_message").click(function(event) {
        show_message_box(username);
        event.preventDefault();
    });

    $("#user_popup_user_information").click(function(event) {
        alert("hello, world!");
        event.preventDefault();
    });

    $("#user_popup_add_blacklist").click(function(event) {
        $.post("/blacklist/add/", {blacklist_id: username},
            function(data) {
                alert("Added " + username + " to blacklist.");
            }
        );
        event.preventDefault();
    });

    $("html").click(function(event) {
        $("#user_popup").hide("fast");
		$("#login_box").hide("fast");
    });

    function show_message_box(username) {
        message_popup.show(); 
        $("#message_receiver_field").val(username);
    }
    $("#message_submit").click(function(event) {
        $.post("/message/send/", {receiver: $("#message_receiver_field").val(), text: $("#message_text_field").val(), ajax:"1"},
            function(data){
                alert(data);
            });
        event.preventDefault();
    });
	/* 로그인 css absolute show로 바꿈
    $("#login_toggle").toggle(
        function () {
            $("#login_textfield").show();
        },
        function () {
            $("#login_textfield").hide();
        }
    );
	*/

//인풋에 포커스 있을때 단축키 작동안함
	$focus_input = 0;

	$("input").focus(function(){
			$focus_input = 1
			});
	$("textarea").focus(function(){
			$focus_input = 1
			});
	$("input").blur(function(){
			$focus_input = 0
			});

//로그인 뜨게함
	$("#login_box").addClass("absolute");
	$("#login_box").hide();
    $("#login_toggle").click(function(event) {

        $("#login_box").css("top", $(this).offset()["top"] + $(this).height());
        $("#login_box").css("left", $(this).offset()["left"] - 400);

        $("#login_box").show("fast");
		$("#login_username_field").focus();
        event.stopPropagation(); 
		event.preventDefault();
    });
});
