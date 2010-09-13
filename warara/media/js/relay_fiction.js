$(document).ready(function(){
    $(".article_reply textarea").autoResize({
        onResize : function() { },
        animateCallback : function() { },
        animateDuration : 0,
        extraSpace : 0
    });

    $root_article_id = parseInt($("#root_article_info").attr("rel"));
    $row_count = $("#article_table tr").length;
    $(document).keypress(function(event) {
        if($focus_input || event.altKey || event.ctrlKey){
        return;
        }
        switch (event.which) {
            case 108:  // list
                var list_link = $("#list_link").attr("href");
                location.href = list_link;
                break;
        }
    });

    $(".article_content").hover(
        function() {
            $(this).children(".article_info,.article_read_buttons").fadeIn(50);
        },
        function(event) {
            $(this).children(".article_info,.article_read_buttons").fadeOut(50);
        }
    );

    $(".article div.article_content.previously_read").hide();

    $move_article_read = function($article_pos){
        if($article_pos > 0 && $article_pos <= $row_count){
            var article_link = $("#article_table tr").eq($article_pos).children(".title_col").children("a").attr("href");
            location.href = article_link;
        }
        else if($article_pos == 0){
        }
        else if($article_pos > $row_count){
        }
    }

    $(".article_vote").click(function(event){
            var vote_url = $(this).attr("href");
            if ($(this).attr("name") == "article_vote_up")
                $vote_num = $(".positive_vote_num_" + $(this).attr("rel"));
            else
                $vote_num = $(".negative_vote_num_" + $(this).attr("rel"));
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
    $("textarea[name='content']").focus(function(){
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
                    location.href = $("#list_link").attr("href");
                    break;
            }
        });

    $(".write_reply.small_btn").click(function(event) {
        $(this).parent().submit();
        $(this).attr("disabled", "disabled");
    });

    $("#color_picker_trigger").click( function(){
        $("#color_picker").toggle();
    });

    $("#color_picker").farbtastic("#reply_color");
    var color_picker = $.farbtastic($("#color_picker"));
    color_picker.linkTo( function(color) {
        $("#color_picker_trigger").css('background-color', color);
        $(".article_reply textarea").css('color', color);
        $(".article_reply textarea").css('border-color', color);
    });
});
