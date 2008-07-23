
$(document).ready(function(){
    $(".article_reply").hide();
    $(".article_reply_show").click(function(event) {
        $(this).parent().children(".article_reply").toggle("fast");
        event.preventDefault();
    });

    $(document).keypress(function(event) {
        switch (event.which) {
            case 108:  // list
                var list_link = $("#list_link").attr("href");
                location.href = list_link;
                break;
        }
    });
});
