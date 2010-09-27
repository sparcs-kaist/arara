$(document).ready(function(){
    var cursor_pos = 1;
    var original_cursor_pos = -2; // -1 은 커서 없을 때, 이므로.

    if($(".articleInfo").length){ //if it is a read page
    $root_article_id = parseInt($(".articleInfo").attr("rel"));
    cursor_pos = parseInt($("td.articleid[rel='" + $root_article_id + "']").parent().attr("rel"));
    original_cursor_pos = cursor_pos; // XXX root_article_pos 를 쓸 필요가 있는가?
    $root_article_pos = cursor_pos; //naming
    }
    var row_count = $(".boardList tr").length;
	if(!$logged_in){
	cursor_pos = -1;
	}
    update_table(cursor_pos);
    function update_table(cursor_pos) {
        if(cursor_pos >= 0){
        $(".boardList tr").removeClass("selected");
        $(".boardList tr").eq(cursor_pos).addClass("selected");
        }
    }
    function read_article() {
        //$.history.load(cursor_pos);
        var article_link = $(".boardList tr").eq(cursor_pos).children(".title").children("a").attr("href");
        location.href = article_link;
    }

    var cursor_sm = 0; //cursor search method
    var length_sm = $(".searchBox a").length;

    function update_search_method(cursor){
        $(".searchBox a").removeClass("highlight");
        $(".searchBox a").eq(cursor).addClass("highlight");
    }

    $(".searchBox a").click(function(event){
            toggle_search_method($(this));
            event.preventDefault();
            });

    function toggle_search_method($sm){
            $sm.toggleClass("selected");
            if($sm.hasClass("selected")){
            $sm.next().attr("name", $sm.attr("rel"));
            }
            else{
            $sm.next().removeAttr("name");
            }
/*            if(!$(".selected").length){
            $("#board_buttons span a[name='search_method_select']").eq(((cursor_pos-1) % 4)).addClass("selected");
            $("#board_buttons span.search_method input").eq(((cursor_pos-1) % 4)).attr("name", $("#board_buttons span a[name='search_method_select']").eq(((cursor_pos-1) % 4)).attr("rel"));
            }*/
    }

    $(document).keypress(function(event) {
		if($focus_input || event.altKey || event.ctrlKey){
		return;
		}
        if(!$(".articleView").length){ //move to main page when user press q in article_list page
        switch(event.which){
            case 113: // 'q'
                location.href = "/main";
                break;
                }
        }
        // Search에 관한 부분
        if($(".searchBox a.highlight").length){
            switch(event.which){
                case 115: // 's'
                    $(".searchBox a.highlight").removeClass("highlight");
                    $(".boardList .hidden_selected").removeClass("hidden_selected").addClass("selected");
                    $(".searchBox input[name='searchText']").focus();
                    cursor_sm = 0;
                    break;
                case 106: // 'j'
                    cursor_sm -= 1;
                    if (cursor_sm < 0){
                    cursor_sm = 0;
                    }
                    update_search_method(cursor_sm);
                    break;
                case 107: 'k'
                    cursor_sm += 1;
                    if (cursor_sm >= length_sm){
                    cursor_sm = length_sm - 1;
                    }
                    update_search_method(cursor_sm);
                    break;
                case 32:
                case 39:
                    $sm = $(".searchBox a").eq(cursor_sm);
                    toggle_search_method($sm);
                    event.preventDefault();
                    break;
            }
        }
        else{
            switch(event.which){
                case 115:
                    $(".highlight").removeClass("highlight");
                    $(".boardList .selected").removeClass("selected").addClass("hidden_selected");
                    $(".searchBox a").eq(cursor_sm).addClass("highlight");
                    location.href = "#search_method_select";
                    break;
            }
        }
        if($(".boardList tr.selected").length){
            switch (event.which) {
                case 32:  // space
                    if (cursor_pos != original_cursor_pos){
                        event.preventDefault();
                        read_article();
                    }
                    break;
                case 13:  // enter
                case 39:
                case 105:
                    event.preventDefault();
                    read_article();
                    break;
                case 106:  // j
                    cursor_pos += 1;
                    if (cursor_pos >= row_count) cursor_pos = row_count - 1;
                    update_table(cursor_pos);
                    break;
                case 107:  // k
                    cursor_pos -= 1;
                    if (cursor_pos < 1) cursor_pos = 1;
                    update_table(cursor_pos);
                    break;
                case 78: // N
                    //일단 되는 경우만 생각하고 짜보자
                    //cursor_pos = 0;
                    //location.href = 
                    if(!($("#now_page").is(":last-child"))) location.href = $("#now_page").next().attr("href");
                    break;
                case 80: // P
                    if(!($("#now_page").is(":first-child"))) location.href = $("#now_page").prev().attr("href");
                    break;
                case 98:
                    $show_user_popup($(".boardList tr .author").eq(cursor_pos-1));
                    $focus_user_popup();
                    break;
                case 82:
                    location.href = $("#writeForm").attr("action");
                    break;
                default:
                    //alert(event.which);
            }
		}
    });

    // search에 관한 부분임
    $(".heading_list").change(function() {
        if ($("#board_search_content").val() != "")
            $("#board_search_submit").click();
        else if ($(".heading_list > option:selected").attr('name') == "all")
        {
            var redirection_url = decodeURIComponent(location.href);
            
            redirection_url = redirection_url.substring(0, redirection_url.indexOf('?'));

            $(location).attr('href', redirection_url);
        }
        else
            $("#heading_search").submit();
    });

    $("#board_search_submit").click(function() {
        var searchHeading = $(".heading_list > option:selected").val();

        if ($(".heading_list > option:selected").attr('name') == "all")
            $("#board_search_heading").attr('disabled', 'disabled');
        else
            $("#board_search_heading").attr('value', searchHeading);
    });
});
