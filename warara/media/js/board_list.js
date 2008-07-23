$(document).ready(function(){
    var cursor_pos = 1;
    var row_count = $("#article_table tr").length;
    $.history.init(function(hash) {
        if (hash) {
            cursor_pos = parseInt(hash);
            if (cursor_pos == -1)
                cursor_pos = row_count - 1;
        }
    });


    update_table(cursor_pos);
    function update_table(cursor_pos) {
        $("#article_table tr").removeClass("row_highlight");
        $("#article_table tr").eq(cursor_pos).addClass("row_highlight");
    }
    function read_article() {
        $.history.load(cursor_pos);
        var article_link = $("#article_table tr").eq(cursor_pos).children(".title_col").children("a").attr("href");
        location.href = article_link;
    }

    $(document).keypress(function(event) {
        switch (event.which) {
            case 13:  // enter
            case 32:  // space
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
            default:
                //alert(event.which);
        }
    });
});
