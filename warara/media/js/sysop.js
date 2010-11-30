var selected_board;

function request_action(action){
    if(selected_board == null) return;
    if(action == "toggle_hide"){
        if(selected_board.is_hidden == true) action = "return_hide";
        else if(selected_board.is_hidden == false) action = "hide";
    }
    request = { type: "POST", async: false, success: update_list }
    if(action == "edit"){
        request.url = "/sysop/edit_board/";
        request.data = { orig_board_name : selected_board.board_name, 
                         new_board_name : $("#board_name").val(), 
                         new_alias : $("#alias").val(),
                         new_board_description : $("#board_description").val(),
                         new_category_name : $("#board_category").val() };
    } else if(action == "change_auth_mode"){
	request.url = "/sysop/change_auth/";
	request.data = { orig_board_name : selected_board.board_name,
	                 change_read_level : $("#change_read_level").val(),
	                 change_write_level : $("#change_write_level").val() };
    } else if(action == "add_bbs_manager"){
	request.url = "/sysop/add_bbs_manager/";
	request.data = { board_name : selected_board.board_name,
		         manager : $("#manager").val() };
    } else if(action == "remove_bbs_manager"){
        request.url = "/sysop/remove_bbs_manager/";
        request.data = { board_name : selected_board.board_name,
                         manager : $("#manager").val() };
    } else {
        request.url = "/sysop/modify_board/";
        request.data = { action : action,
                         board_name : selected_board.board_name };
    }
    $.ajax(request);
}

function update_list(data){
    var splited_data = data.split("\n");
    var response_message = splited_data[0].split("\t")[0]
    if(response_message != "SUCCESS"){
        alert("Failed to apply changes!");
        location.reload(true);
    }

    document.location.reload();

    var action_done = splited_data[0].split("\t")[1];
    if(action_done == "hide" || action_done == "return_hide"){
        $("#board_actions li:nth-child(1) a").html((action_done == "hide" ? "보이기" : "숨기기"));
        selected_board.is_hidden = (action_done == "hide")
    } else if(action_done == "remove"){
        $("#board_actions").hide();
        $("#edit_board").hide();
        $("#change_auth").hide();
	$("#add_manager").hide();
        selected_board = null;
    } else if(action_done == "edit"){
        selected_board.board_name = splited_data[0].split("\t")[2];
    }

    $("#all_board_list tbody").empty();

    for(i=1;i<splited_data.length;i++){
        board = splited_data[i].split("\t");

        if(selected_board != null && board[0] == selected_board.board_name){
            $("#all_board_list tbody").append('<tr class="' + board[3] + ' selected_board"><td>' + board[0] + "</td><td>" + board[1] + '</td><td>' + board[2] + '</td><td>' + board[4] + '</td><td>' + board[5] + '</td><td>' + board[6] + '</td><td>' + board[7] + '</td><td><a href="/board/' + board[0] + '" target="_blank">Link</a></td></tr>');
        } else {
            $("#all_board_list tbody").append('<tr class="' + board[3] + '"><td>' + board[0] + '</td><td>' + board[1]  + '</td><td>' + board[2] + '</td><td>' + board[4] + '</td><td>' + board[5] + '</td><td>' + board[6] + '</td><td>' + board[7] + '</td><td><a href="/board/' + board[0] + '" target="_blank">Link</a></td></tr>');
        }
    }
    set_item_action();
}

function set_item_action(){
    $("#all_board_list tbody tr").click( function(event) {
        $("#board_actions").show();
        $("#edit_board").show();
        $("#change_auth").show();
        $("#add_manager").show();

        var is_hidden = $(this).attr("class").indexOf("hidden_board") != -1;
        var board_name = $(this).children(":nth-child(1)").html();
        var alias = $(this).children(":nth-child(2)").html();
        var board_description = $(this).children(":nth-child(3)").html();
        var board_read_level = $(this).children(":nth-child(4)").html();
        var board_write_level = $(this).children(":nth-child(5)").html();
        var board_category = $(this).children(":nth-child(7)").html();
        if(board_category == '') board_category = 'None';
        $("#board_actions li:nth-child(1) a").html(is_hidden?"보이기":"숨기기");
        // 현재 보드 설정값 가져와 셋팅하기
        $("#board_name").val(board_name);
        $("#alias").val(alias);
        $("#board_description").val(board_description);
        $("#change_read_level").val(board_read_level);
        $("#change_write_level").val(board_write_level);
        $("#board_category > option[value=\"" + board_category + "\"]").attr("selected", "true");

        selected_board = { board_name : board_name, is_hidden : is_hidden };
        
        $("#all_board_list tbody tr").removeClass("selected_board");
        $(this).addClass("selected_board");
    });
    $("#all_board_list tbody tr").hover( function() { $(this).addClass("hovering_board"); }, function() { $(this).removeClass("hovering_board"); });
}

$(document).ready( function() {
    $("#board_actions").hide();
    $("#edit_board").hide();
    $("#change_auth").hide();
    $("#add_manager").hide();

    // 숨기기/보이기 버튼
    $("#board_actions li:nth-child(1) a").unbind()
    $("#board_actions li:nth-child(1) a").click( function(event) {
        event.preventDefault();
        request_action("toggle_hide");
    });

    // 삭제 버튼
    $("#board_actions li:nth-child(2) a").unbind()
    $("#board_actions li:nth-child(2) a").click( function(event) {
        event.preventDefault();
        request_action("remove");
    });

    // 보드 이름/설명 적용 버튼
    $("#apply_changes").unbind();
    $("#apply_changes").click( function(event) {
        event.preventDefault();
        request_action("edit");
    });

    // 사용권한 설정
    $("#apply_change_auth").unbind();
    $("#apply_change_auth").click( function(event) {
	event.preventDefault();
	request_action("change_auth_mode");
    });

    // 관리자 추가 버튼
    $("#apply_add_manager").unbind();
    $("#apply_add_manager").click( function(event) {
        event.preventDefault();
        request_action("add_bbs_manager");
    });

    // 관리자 제거 버튼  
    $("#apply_remove_manager").unbind();
    $("#apply_remove_manager").click( function(event) {
        event.preventDefault();
        request_action("remove_bbs_manager");
    });

    // 위로 버튼
    $("#board_actions li:nth-child(3) a").unbind()
    $("#board_actions li:nth-child(3) a").click( function(event) {
        event.preventDefault();
        request_action("moveup");
    });

    // 아래로 버튼
    $("#board_actions li:nth-child(4) a").unbind()
    $("#board_actions li:nth-child(4) a").click( function(event) {
        event.preventDefault();
        request_action("movedown");
    });

    set_item_action();

    selected_board = null;
});
