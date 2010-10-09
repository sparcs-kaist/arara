$(document).ready(function(){
    // XXX(serialx): Too many quirks to be useful
    //$(".article_reply textarea").resizable({handles: 's', grid: [50, 50]});
    //$(".article_reply .ui-wrapper").css('height', '');
    //$(".article_reply .ui-wrapper").css('width', '');

    $(".addReply textarea").autoResize({
        onResize : function() { },
        animateCallback : function() { },
        animateDuration : 50,
        extraSpace : 20
    });

    $(".addReply").hide();
    $(".articleButtons .reply").click(function(event) {
        // 만약 다른 곳에 있던 답글 상자를 가져와야 하는 경우라면
        if($(this).parent().parent().children(".addReply").length == 0){
            var board_name = $(this).parent().children("#board_name").val();
            var article_id = $(this).parent().children("#article_id").val();
            var reply_url = "/board/" + board_name + "/" + article_id + "/reply/";

            p = $(".addReply").hide().detach().insertAfter($(this).parent());
            p.toggle("fast");
            p.children().children("input[name='article_no']").val(article_id);
            p.children().attr('action', reply_url);
        }
        // 그렇지 않을 경우 toggle만
        else {
            $(".addReply").toggle("fast");
        }
        event.preventDefault();
    });

    $root_article_id = parseInt($(".articleInfo").eq(0).attr("rel"));
    $row_count = $(".articleList tr").length;

        $(document).keypress(function(event) {
        if($focus_input || event.altKey || event.ctrlKey){
        return;
        }
        switch (event.which) {
            case 108:  // list
                var backref = $("#backref").val();
                location.href = backref;
                break;
        }
    });

// XXX(hodduc): 동작하고 있지 않은 기능인 듯?
//    $(".article div.article_content.previously_read").hide();

    $(".replyTitle h4 a").click(function(event) {
        $(this).parent().parent().parent().children("div.replyContents").toggle("fast");
        event.preventDefault();
    });
    $(".articleTitle h3 a").click(function(event) {
        $(this).parent().parent().parent().children("div.articleContents").toggle("fast");
        event.preventDefault();
    });

    $file_no = 1;

    function create_more_attach_form(this_select, event){
        $file_no++;

        var new_attach = this_select.parent().parent().clone();
        var new_attach_id = "write_reply_attach_" + $file_no;
        
        new_attach.children("th").children("label").attr("for", new_attach_id).text("첨부" + $file_no);
        new_attach.children("td").children("input").attr("name", new_attach_id).attr("id", new_attach_id);
        new_attach.children("td").children("input").html(new_attach.children("td input").html()); //reset the input field
        new_attach.children("td").children("a").click(function(event){
            create_more_attach_form($(this), event);
        });

        this_select.parent().parent().after(new_attach);
        this_select.after(
            $('<a class="file_delete" href="#">삭제</a>').click(function(event){
                $(this).parent().parent().remove();
                event.preventDefault();
            })
        );

        this_select.remove();
        event.preventDefault();
    }
        
    $(".arAttach #attach_more").click(function(event){
        create_more_attach_form($(this), event);
    });


/* XXX(hodduc) Cancel Reply는 새 디자인에서 삭제된 기능임
    $("input.cancel_reply").click(function(){
            $(this).parent().parent().hide();
            $(this).parent().children("ul").children("li").children("input[name='title']").val("");
            $(this).parent().children("ul").children("li").children("textarea").val("");
            });
*/

/* XXX(hodduc) Resizing은 작동하지 않음.
 * 굳이 필요한지 의문.
    $(".attached img").load(function(){
        var this_width = $(this).width()
        $(this).width(10);
        var parent_width = $(this).parent().width();
        if(this_width > parent_width){
            $(this).width(parent_width);
        }
        else {
            $(this).width(this_width);
        }
    });
*/

    $move_article_read = function($article_pos){
        if($article_pos > 0 && $article_pos <= $row_count){
            var article_link = $(".articleList tr").eq($article_pos).children(".title").children("a").attr("href");
            location.href = article_link;
        }
        else if($article_pos == 0){
        }
        else if($article_pos > $row_count){
        }
    }
    
    $(".articleButtons .modify").click(function(event){
            var board_name = $(this).parent().children("#board_name").val();
            var article_id = $(this).parent().children("#article_id").val();
            var modify_url = "/board/" + board_name + "/write?article_id=" + article_id;
            location.href = modify_url;
    });
    $(".articleButtons .delete").click(function(event){
            var board_name = $(this).parent().children("#board_name").val();
            var root_id = $(this).parent().children("#root_id").val();
            var article_id = $(this).parent().children("#article_id").val();
            var delete_url = "/board/" + board_name + "/" + root_id + "/" + article_id + "/delete/";
            location.href = delete_url;
    });
    $(".articleButtons .rec, .articleButtons .dis").click(function(event){
            var board_name = $(this).parent().children("#board_name").val();
            var root_id = $(this).parent().children("#root_id").val();
            var article_id = $(this).parent().children("#article_id").val();
            var vote_url = "/board/" + board_name + "/" + root_id + "/" + article_id + "/vote/";

            if ($(this).hasClass("rec")){
                vote_url = vote_url + '+';
                $vote_num = $("#positive_vote_num_" + article_id);
            }
            else{
                vote_url = vote_url + '-';
                $vote_num = $("#negative_vote_num_" + article_id);
            }
            $.get(vote_url, function(data){
                if(data == "OK"){
                alert("Successfully voted");
                $vote_num.text(parseInt($vote_num.text())+1);
                }
                else if(data == "ALREADY_VOTED"){
                alert("You voted already");
                }
                else{
                alert("Unknown error");
                }
                });
            event.preventDefault();
    });

    $focus_textarea_reply = 0;
    $("#write_reply_content").focus(function(){
            $focus_textarea_reply = $(this);
            });

    $(document).keypress(function(event){
        if($focus_textarea_reply){
            var enterwithshiftkey = event.shiftKey;
            switch(event.which){
                case 13:
                    if(!enterwithshiftkey){
                        break;
                    }
                    if(confirm("send")){
                        $focus_textarea_reply.parent().parent().parent().submit();
                        break;
                    }
                    event.preventDefault();
            }
        }
        if($focus_input || event.altKey || event.ctrlKey){
            return;
        }
        switch(event.which){
            case 113:
                location.href = $("#backref").val();
                break;
        }
    });

    $("#write_reply").click(function(event) {
        $(this).parent().parent().parent().parent().parent().submit();
        $(this).attr("disabled", "disabled");
    });
});

