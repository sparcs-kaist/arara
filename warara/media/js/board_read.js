
$(document).ready(function(){
    $(".article_reply").hide();
    $(".article_reply_show").click(function(event) {
        $(this).parent().children(".article_reply").toggle("fast");
        event.preventDefault();
    });

    $(document).keypress(function(event) {
		if($input_focus){
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

    $(".article h1 a").click(function(event) {
        $(this).parent().parent().children("div.article_content").toggle("fast");
        event.preventDefault();
    });

	$file_no = 1;

	$("input[name='file_input_add']").click(function(){
		$file_no++;
		$file_input_append = "<p name=" + $file_no + ">\n<caption>file " + $file_no + " : </caption>\n<input type=\"file\" name=\"file" + $file_no + "\"></input>\n<input type=\"button\" value=\"-\" name=\"file_input_delete\"></input>\n</p>";
		$(this).parent().parent().append($file_input_append);

		$("input[name='file_input_delete']").click(function(){
			$(this).parent().remove();
			});
		});
});
