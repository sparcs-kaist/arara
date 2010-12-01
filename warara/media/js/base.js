$(document).ready(function(){
    $("#miniLoginID,#miniLoginPassword").keypress( function(event) {
        if(event.keyCode == '13'){
            $("form[name='login']").submit();
            $("#miniLoginId,#miniLoginPassword").unbind();
            event.preventDefault();
        }
    });
    $("#loginBox a").eq(0).click(function(event) {
        $("#miniLoginSubmit").click();
    });

    $("input[name='current_page_url']").val(location.pathname);
    


    // 이하 유저 정보 팝업에 대한 내용이다
    var user_popup = $("#user_popup");
    var message_popup = $("#message_popup");

    $("#user_popup li").hover(
    function(event) {
        $(this).addClass("user_popup_menu_hover");
    },
    function(event) {
        $(this).removeClass("user_popup_menu_hover");
    });

    $(".nickname").hover(
    function(event) {
        $(this).addClass("nickname_highlight");
    },
    function(event) {
        $(this).removeClass("nickname_highlight");
    });

    $popup_x_coor=0;
    $popup_y_coor=0;

    var username;
    $(".nickname").click(function(event) {
        $show_user_popup($(this));
        event.stopPropagation();
        event.preventDefault();
    });

    $show_user_popup = function($tu){
        if(!$tu.hasClass("nickname")){
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
            event.preventDefault();
            message_popup.show();
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
        $.post("/message/send/", {receiver: $("#message_receiver_field").val(), text: $("#message_text_field").val(), ajax:"1", receiver_type:"username"},
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
    
    //message_thickbox
    $("#message_popup input[name='cancel']").click(function(event){
            tb_remove();
            $("#message_popup").hide();
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

    //로그인 안되있을때
    $logged_in = 0
    if($("#loginBox").length){
        $(".username").removeClass("username");
        $logged_in = 0
    }
    else{
        $logged_in = 1
    }



//단축키 작동
/*
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
    }*/
    $focus_content = function(){
        $(".highlight").removeClass("highlight");
        $(".hidden_selected").removeClass("hidden_selected").addClass("selected");
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
/*
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
*/
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
//            case 116: //t
//            focus_board_list();
//            break;
//            기존 아라에서 좌측 Board list로 포커스를 옮기던 단축키. 현재 일시적으로 지원되지 않음
//            case 121: //y
//            focus_topmenu();
//            break;
//            기존 아라에서 상단 메뉴(Help Account Blacklist 등)으로 포커스를 옮기던 단축키. 현재 일시적으로 지원되지 않음
            case 120: //x, 다른 곳에 포커스가 있을 때 글 목록으로 포커스를 되돌려주는 단축키
            $focus_content();
            break;
            case 46: // '.' , 전체 페이지를 위로 스크롤
            $(document).scrollTop($(document).scrollTop() - 50);
            break;
            case 44: // ',' , 전체 페이지를 아래로 스크롤
            $(document).scrollTop($(document).scrollTop() + 50);
            break;
//            case 101:
//            $("#header input[name='ksearch']").focus();
//            break;
//            기존 아라에서 KSearch 창으로 포커스를 옮기던 단축키. 새 디자인에서 KSearch가 항상 떠 있지 않으므로 이 단축키는 사용하지 않음 
            }
            });
/*
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
    });*/

/*
 * TODO: 현재 1. 단축키, 2. 유저인포팝업, 3. 메세지팝업 에 대한 내용이 섞여있음
 * 주석을 잘 달아서 필요없는 부분 쳐내고 필요한 부분 살려 사용해야함
 */
    get_new_message_count_url = "/message/count_new"
    $.get(get_new_message_count_url, function(data){
        $("#countNewMessage").text(data);
    });
});
