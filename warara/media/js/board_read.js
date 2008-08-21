
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
                //location.href = list_link;
                history.go(-1);
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
		$("#file_line_model input.file_upload").attr("name", "file"+$file_no);
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

});
