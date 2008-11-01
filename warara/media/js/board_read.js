$(document).ready(function(){
    $(".article_reply").hide();
    $(".article_reply_show").click(function(event) {
        $(this).parent().parent().children(".article_reply").toggle("fast");
        event.preventDefault();
    });

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

    $(".article_vote").click(function(event){
            var vote_url = $(this).attr("href")
            $.get(vote_url, {precheck:1}, function(data){
                data = parseInt(data);
                if(!data){
                alert("Already voted!");
                }
                else{
                location.href = vote_url;
                }
                });
            event.preventDefault();
            });

    $(document).keypress(function(event){
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

