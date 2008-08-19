
$(document).ready(function(){
    var user_popup = $("#user_popup");
    user_popup.addClass("absolute");
    var message_popup = $("#message_popup");
    message_popup.addClass("absolute");

	$("input[name='current_page_url']").val(location.pathname);

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

	$popup_x_coor=0;
	$popup_y_coor=0;

    var username;
    $(".username").click(function(event) {
		if(!$(this).hasClass("username")){
		return;
		}
        username = $(this).text();
        $("#user_popup #user_popup_username").text("User: " + username);

        $("#user_popup").css("top", $(this).offset()["top"] + $(this).height());
        $("#user_popup").css("left", $(this).offset()["left"]);

		$popup_y_coor = $(this).offset()["top"];
		$popup_x_coor = $(this).offset()["left"];

        $("#user_popup").show("fast");

		$(document).keyup(function(event){
				switch(event.which){
				case 27: //esc
				$("#user_popup").hide("fast");
				tb_remove();
				break;
				}
				});
        event.stopPropagation(); 
    });

    $("#user_popup_send_message").click(function(event) {
        show_message_box(username, event);
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
		if($focus_input){
		return;
		}
        $("#user_popup").hide("fast");
		$("#login_box").hide();
    });

    function show_message_box(username, event) {
		if(event.shiftKey){
			$("#user_popup .thickbox").removeClass("thickbox");
			message_popup.show(); 
		}
        $("#message_receiver_field").val(username);

		$("input[name='message_popup_exit']").click(function(event){
				$("#message_popup").hide();
				});
		$(document).keyup(function(event){
				switch(event.which){
				case 27:
				$("#message_popup").hide("fast");
				break;
				case 70: //f
				$("#message_text_field").focus();
				break;
				}
				});
    }

    $("#message_popup input.message_send_submit").click(function(event) {
		tb_remove();
        $.post("/message/send/", {receiver: $("#message_receiver_field").val(), text: $("#message_text_field").val(), ajax:"1"},
            function(data){
                alert(data);
				$("#user_popup").hide();
				$("#message_popup").hide("fast");
				$("#message_text_field").val("");
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
			if($(this).attr("type") == "checkbox"){
			$focus_input = 0
			}
			});
	$("textarea").focus(function(){
			$focus_input = 1
			});
	$("input").blur(function(){
			$focus_input = 0
			});
	$("textarea").blur(function(){
			$focus_input = 0
			});


	//ksearch
	$("input[name='ksearch_submit']").click(function(event){
			window.open("http://nan.sparcs.org:9000/search?q=" + $("input[name='ksearch']").val());
			event.preventDefault();
			});
	
	//로그인 안되있을때
	$logged_in = 0
	if($("a[name='top_menu_message']").hasClass("hidden")){
		$(".username").removeClass("username");
		$logged_in = 0
	}
	else{
		$logged_in = 1
	}

	//message_thickbox
	$("#message_popup input[name='cancel']").click(function(event){
			tb_remove();
			$("#message_popup").hide();
			});

//로그인 뜨게함
	$("#login_box").addClass("absolute");
	$("#login_box").hide();
    $("#login_toggle").click(function(event) {

        $("#login_box").show();
		$("#login_username_field").focus();
		event.preventDefault();
		event.stopPropagation();
    });

//단축키 작동
	var cursor_bl = 0; //cursor_board_list
	var cursor_tm = 0; //cursor_topmenu
	function focus_topmenu(){
		if(cursor_tm){
			cursor_tm = 0;
			$(".hidden_highlight").removeClass("hidden_highlight").addClass("row_highlight");
			$(".highlight").removeClass("highlight");
			return;
		}

		cursor_tm = 1;
		$(".highlight").removeClass("highlight");
		$(".row_highlight").removeClass("row_highlight").addClass("hidden_highlight");
		$("#top_menu a[class!='hidden']").eq(cursor_tm-1).addClass("highlight");
		a_tm_length = $("#top_menu a[class!='hidden']").length;
	}
	function focus_board_list(){
		if(cursor_bl){
			cursor_bl = 0;
			$(".hidden_highlight").removeClass("hidden_highlight").addClass("row_highlight");
			$(".highlight").removeClass("highlight");
			return;
		}

		cursor_bl = 1;
		$(".highlight").removeClass("highlight");
		$(".row_highlight").removeClass("row_highlight").addClass("hidden_highlight");
		$("#menu a[class!='hidden']").eq(cursor_bl-1).addClass("highlight");
		a_bl_length = $("#menu a[class!='hidden']").length;
	}
	function move_next(cursor, il){
		if(cursor < il){
			cursor++;
		}
		return cursor;
	}
	function move_prev(cursor, il){
		if(cursor > 1){
			cursor--;
		}
		return cursor;
	}
	function update_highlight(div, cursor){
		$(div + " a[class='highlight']").removeClass("highlight");
		$(div + " a[class!='hidden']").eq(cursor-1).addClass("highlight");
	}
	function focus_content(){
		$(".highlight").removeClass("highlight");
		$(".hidden_highlight").removeClass("hidden_highlight").addClass("row_highlight");
	}

	$(document).keypress(function(event){
			if(!$("#menu a[class='highlight']").length){
			cursor_bl=0;
			return;
			}
			if($focus_input || !cursor_bl){
			return;
			}
			if(event.ctrlKey || event.altKey){
			return;
			}
			switch(event.which){
			case 106: //j
			cursor_bl = move_next(cursor_bl, a_bl_length);
			update_highlight("#menu", cursor_bl);
			break;
			case 107: //k
			cursor_bl = move_prev(cursor_bl, a_bl_length);
			update_highlight("#menu", cursor_bl);
			break;
			case 32: //spacs
			location.href = $("#menu a[class!='hidden']").eq(cursor_bl-1).attr("href");
			break;
			}
			});
	$(document).keypress(function(event){
			if(!$("#top_menu a[class='highlight']").length){
			cursor_tm=0;
			return;
			}
			if($focus_input || !cursor_tm){
			return;
			}
			if(event.ctrlKey || event.altKey){
			return;
			}
			switch(event.which){
			case 107: //j
			cursor_tm = move_next(cursor_tm, a_tm_length);
			update_highlight("#top_menu", cursor_tm);
			break;
			case 106: //k
			cursor_tm = move_prev(cursor_tm, a_tm_length);
			update_highlight("#top_menu", cursor_tm);
			break;
			case 32: //spacs
			location.href = $("#top_menu a[class!='hidden']").eq(cursor_tm-1).attr("href");
			break;
			}
			});
	$(document).keypress(function(event){
			if(event.ctrlKey || event.altKey){
			return;
			}

			if($focus_input){
			switch(event.which){
			case 27: //esc
			$focus_input = 0;
			break;
			}
			return;
			}

			switch(event.which){
			case 116: //t
			focus_board_list();
			break;
			case 121: //y
			focus_topmenu();
			break;
			case 120: //x
			focus_content();
			break;
			}
			});
});
