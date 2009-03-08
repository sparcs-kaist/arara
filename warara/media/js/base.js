$(document).ready(function(){
    $("#more_link").hide();
    $("#more_link_over").click(function(event) {
        $("#more_link").show();
        $("#more_link_over").hide();
    });
    $("#less_link_over").click(function(event) {
        $("#more_link").hide();
        $("#more_link_over").show();
    });

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
        $show_user_popup($(this));
        event.stopPropagation(); 
    });

    $show_user_popup = function($tu){
		if(!$tu.hasClass("username")){
		return;
		}
        username = $tu.text();
        $("#user_popup #user_popup_username").text("User: " + username);

        $("#user_popup").css("top", $tu.offset()["top"] + $tu.height());
        $("#user_popup").css("left", $tu.offset()["left"]);

		$popup_y_coor = $tu.offset()["top"];
		$popup_x_coor = $tu.offset()["left"];

        $("#user_popup").show("fast");

		$(document).keyup(function(event){
				switch(event.which){
				case 27: //esc
				$("#user_popup").hide("fast");
				tb_remove();
                if($("#user_popup .highlight").length){
                $focus_user_popup();
                }
				break;
				}
				});

    }

    $("#user_popup_send_message").click(function(event) {
        show_message_box(username, event);
        event.preventDefault();
    });

    $("#user_popup_user_information").click(function(event) {
            show_user_info_popup(event);
    });

    function show_user_info_popup(event){
        $("#user_information_popup_content").contents().remove();
        if(event.shiftKey) {
            $("#user_information_popup").show("fast"); 
        }
        $.post("/main/userinfo/", {query_user_name: username},
            function(data, textStatus) {
                if(data == 0){
                    alert("알수없는에러");
                    $("#user_information_popup").hide();
                }
                else{
                    $(data).appendTo("#user_information_popup_content");
                }
            }
        );
        $(document).keyup(function(event) {
            if(event.keyCode == 27) {
                if($("#u_info_pop_head:visible").length){
                    $(".hidden_highlight").removeClass("hidden_highlight").addClass("row_highlight");
                    }
                $("#user_information_popup").hide("fast");
            }
        });
        event.preventDefault();
        $("#user_information_close").click(function(event) {
            tb_remove(); 
            $("#user_information_popup").hide("fast");
        });
        $("#u_info_add_blacklist").click(function(event) {
            add_blacklist();
            event.preventDefault();
        });
        $("#u_info_send_message").click(function(event) {
            tb_remove(); 
            $("#user_information_popup").hide("fast");
            $("#message_popup").show("fast");
            event.preventDefault();
            $("#message_receiver_field").val(username);
        });
    }
    function add_blacklist(){
        $.post("/blacklist/add/", {blacklist_id: username, ajax:1},
            function(data, textStatus) {
                if(data == "ALREADY_ADDED"){
                alert("already added");
                }
                else if(data == "CANNOT_ADD_YOURSELF"){
                alert("cannot add yourself");
                }
                else if(data == 1){
                alert("Added " + username + " to blacklist.");
                }
                else{
                alert("알수없는에러");
                }
                $(".hidden_highlight").removeClass("hidden_highlight").addClass("row_highlight");
            }
        );
    }

    $("#user_popup_add_blacklist").click(function(event) {
        add_blacklist();
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
			message_popup.show(); 
		}
        $("#message_receiver_field").val(username);

		$("input[name='message_popup_exit']").click(function(event){
				$("#message_popup").hide();
				});
    }

    $("#message_popup input.message_send_submit").click(function(event) {
		tb_remove();
        $.post("/message/send/", {receiver: $("#message_receiver_field").val(), text: $("#message_text_field").val(), ajax:"1", receiver_type:"nickname"},
            function(data){
                if(data == 1){
                    alert("Message send successful!");
                    $(".hidden_highlight").removeClass("hidden_highlight").addClass("row_highlight")
                    $("#user_popup").hide();
                    $("#message_popup").hide("fast");
                    $("#message_text_field").val("");
                }
                else{
                alert("알수없는에러");
                }
            });
        event.preventDefault();
    });

//인풋에 포커스 있을때 단축키 작동안함
	$focus_input = 0;

	$("input[type='text']").focus(function(){
			$focus_input = 1;
			});
    $("input[type='password']").focus(function(){
            $focus_input = 1;
            });
    $("input[type='submit']").focus(function(){
            $focus_input = 1;
            });
	$("textarea").focus(function(){
			$focus_input = 1;
			});
	$("input").blur(function(){
			$focus_input = 0;
			});
	$("textarea").blur(function(){
			$focus_input = 0;
			});

    //png fix
    //$(".iepngfix").pngfix();

	//ksearch
	$("input[name='ksearch_submit']").click(function(event){
			window.open("http://ksearch.sparcs.org/search?q=" + $("input[name='ksearch']").val());
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

    //login error check
    /*$("#login_box input[type='submit']").click(function(event){
            var login_username = $("#login_box input[name='username']").val();
            var login_password = $("#login_box input[name='password']").val();
            $.post("/account/login/", {username:login_username, password:login_password, precheck:1}
                , function(data){
                /*if(data == "WRONG_USERNAME"){
                alert("Id doesn't exist");
                }
                else if(data == "wrong password"){
                alert("Enter the correct password");
                }
                else if(data == "not activated"){
                alert("Please check your E-mail");
                }
                else if(data == "LOGIN_FAILED"){
                alert("dataafjewiofjaweiofj");
                }
                else{
                document.login.submit();
                }
                });
            event.preventDefault();
            });
    */
	//logout function
    function logout(){
			$.get("/account/logout", function(data){
                $("#top_menu a.hidden").removeClass("hidden");
				$("#top_menu a[name='logout']").hide();
				$("#top_menu a[name='login']").show();
				$("#top_menu a[name='account']").hide();
				$("#top_menu a[name='register']").show();
				$("#top_menu a[name='top_menu_message']").hide();
				$("#top_menu a[name='blacklist']").hide();
				});
    }
	$("a[name='logout']").click(function(event){
            logout();
			event.preventDefault();
			});

//단축키 작동
	var cursor_bl = 0; //cursor_board_list
	var cursor_tm = 0; //cursor_topmenu
    var cursor_up = 0; //cursor_user_popup
    var a_up_length = 0;
    var hidden_cursor_bl = 1;

    $("#menu li a").each(function(){ // set initial cursor_bl
            if($(this).text() == $("#bbsname").text()){
            hidden_cursor_bl = parseInt($(this).parent().attr("rel"));
            }
            });

    $focus_user_popup = function(){
        if(cursor_up){
            cursor_up = 0;
			$(".hidden_highlight").removeClass("hidden_highlight").addClass("row_highlight");
			$(".highlight").removeClass("highlight");
			return;
        }
        cursor_up = 1;
        $(".highlight").removeClass("highlight");
        $(".row_highlight").removeClass("row_highlight").addClass("hidden_highlight");
        $("#user_popup li.user_popup_function:visible").eq(cursor_up-1).addClass("highlight");
        a_up_length = $("#user_popup li.user_popup_function:visible").length;
    }

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
		$("#top_menu a:visible").eq(cursor_tm-1).addClass("highlight");
		a_tm_length = $("#top_menu a:visible").length;
	}
	function focus_board_list(){
		if(cursor_bl){
            hidden_cursor_bl = cursor_bl;
			cursor_bl = 0;
			$(".hidden_highlight").removeClass("hidden_highlight").addClass("row_highlight");
			$(".highlight").removeClass("highlight");
			return;
		}

		cursor_bl = hidden_cursor_bl;
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
		$(div + ".highlight").removeClass("highlight");
		$(div + ":visible").eq(cursor-1).addClass("highlight");
	}
	$focus_content = function(){
		$(".highlight").removeClass("highlight");
		$(".hidden_highlight").removeClass("hidden_highlight").addClass("row_highlight");
	}
    function popup_function(event){
        $fn = $("#user_popup li.user_popup_function a").eq(cursor_up-1).attr("id");
        cursor_up = 0;
        $(".highlight").removeClass("highlight");
        $("#user_popup").hide();
        if($fn == "user_popup_send_message"){
            event.shiftKey = 1;
            show_message_box(username, event);
        }
        else if($fn == "user_popup_user_information"){
            event.shiftKey = 1;
            show_user_info_popup(event);
        }
        else if($fn == "user_popup_add_blacklist"){
            add_blacklist();
        }
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
			update_highlight("#menu a", cursor_bl);
			break;
			case 107: //k
			cursor_bl = move_prev(cursor_bl, a_bl_length);
			update_highlight("#menu a", cursor_bl);
			break;
			case 32: //spacs
            case 39:
			location.href = $("#menu a[class!='hidden']").eq(cursor_bl-1).attr("href");
            event.preventDefault();
			break;
			}
			});
	$(document).keypress(function(event){
            if(!$("#top_menu a").hasClass("highlight")){
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
			case 106: //j
			cursor_tm = move_next(cursor_tm, a_tm_length);
			update_highlight("#top_menu a", cursor_tm);
			break;
			case 107: //k
			cursor_tm = move_prev(cursor_tm, a_tm_length);
			update_highlight("#top_menu a", cursor_tm);
			break;
			case 32: //spacs
            if($("#login_box:visible").length){
                break;
            }
            case 39:
            if($("#top_menu a[name='login']").hasClass("highlight")){
                $("#login_box").show();
                $("#login_username_field").focus();
                event.preventDefault();
                break;
            }
            else if($("#top_menu a[name='logout']").hasClass("highlight")){
                $(".highlight").removeClass("highlight");
                cursor_tm = 0;
                logout();
                event.preventDefault();
                break;
            }
			location.href = $("#top_menu a:visible").eq(cursor_tm-1).attr("href");
			break;
			}
			});
    $(document).keypress(function(event){
            if(!$("#user_popup li.highlight").length){
            cursor_up = 0;
            return;
            }
			if($focus_input || !cursor_up){
			return;
			}
			if(event.ctrlKey || event.altKey){
			return;
			}
			switch(event.which){
			case 106:
			cursor_up = move_next(cursor_up, a_up_length);
			update_highlight("#user_popup li.user_popup_function", cursor_up);
			break;
			case 107:
			cursor_up = move_prev(cursor_up, a_up_length);
			update_highlight("#user_popup li.user_popup_function", cursor_up);
			break;
            case 32:
            case 39:
            event.preventDefault();
            popup_function(event);
            break;
            case 27:
            focus_user_popup();
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
			$focus_content();
			break;
            case 46:
            $(document).scrollTop($(document).scrollTop() - 50);
            break;
            case 44:
            $(document).scrollTop($(document).scrollTop() + 50);
            break;
            case 101:
            $("#header input[name='ksearch']").focus();
            break;
			}
			});

    $(document).keypress(function(event){
        if($("#user_information_popup:visible").length){
            switch(event.which){
                case 66:
                    add_blacklist();
                    $(".hidden_highlight").removeClass("hidden_highlight").addClass("row_highlight");
                    $("#user_information_popup").hide("fast");
                    event.preventDefault();
                    break;
            }
        }
    });

    $(document).keyup(function(event){
        if($("#message_popup:visible").length){
            switch(event.which){
            case 27:
            $("#message_popup").hide("fast");
            $(".hidden_highlight").removeClass("hidden_highlight").addClass("row_highlight");
            break;
            case 70: //f
            if($("#message_popup_content:visible").length){
            $("#message_text_field").focus();
            }
            break;
            }
        }
    });
});
