$(document).ready(function(){
    // XXX(serialx): Too many quirks to be useful
    //$(".article_reply textarea").resizable({handles: 's', grid: [50, 50]});
    //$(".article_reply .ui-wrapper").css('height', '');
    //$(".article_reply .ui-wrapper").css('width', '');


    // Dynamically resize the reply textarea
    var resize = function() {
        var size = this.scrollHeight;
        var minheight = 100;
        var maxheight = 500;
        if (size > minheight && size < maxheight)
            $(this).height(size);
        if (size > maxheight)
            $(this).height(maxheight);
    }

    $(".article_reply textarea").change(resize).keyup(resize);

    $(".article_reply").hide();
    $(".article_reply_show").click(function(event) {
        $(this).parent().parent().children(".article_reply").toggle("fast");
        event.preventDefault();
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

    $(".article div.article_content.previously_read").hide();

    $(".article_reply_title h1 a").click(function(event) {
        $(this).parent().parent().parent().children("div.article_content").toggle("fast");
        event.preventDefault();
    });
    $("h1.root_article_title a").click(function(event) {
        $(this).parent().parent().children("div.article_content").toggle("fast");
        event.preventDefault();
    });

    $file_no = 1;

    $("input[name='file_input_add']").click(function(){
		$file_no++;
		$("#file_line_model span.article_write_file_caption").text("file " + $file_no);
		$("#file_line_model .file_upload_t input[type='file']").remove();
		var file_append = "<input type=\"file\" name=\"file" + $file_no + "\" class=\"file_upload\" size=\"95\"></input>";
		$("#file_line_model .file_upload_t").append(file_append);
		$("#article_write_file").append($("#file_line_model").contents().clone());
        $(this).parent().parent().parent().append($("#file_line_model").contents().clone());

        $("input[name='file_input_delete']").click(function(){
            $(this).parent().parent().remove();
            });

        $("input.file_upload").change(function(){
            $(this).parent().parent().children("div.file_upload_f").children("input.file_input_f").val($(this).val());
            });
        });

    $("input.file_upload").change(function(){
        $(this).parent().parent().children("div.file_upload_f").children("input.file_input_f").val($(this).val());
        });

    $("input.cancel_reply").click(function(){
            $(this).parent().parent().hide();
            $(this).parent().children("ul").children("li").children("input[name='title']").val("");
            $(this).parent().children("ul").children("li").children("textarea").val("");
            });
    
    $(".article_content img").load(function(){
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
            $vote_num = $(".vote_num_" + $(this).attr("rel"));
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

});

