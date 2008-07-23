
$(document).ready(function(){
    $(".article_reply").hide();
    $(".article_reply_show").click(function(event) {
        $(this).parent().children(".article_reply").toggle("fast");
        event.preventDefault();
    });
});
