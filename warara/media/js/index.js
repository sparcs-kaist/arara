$(document).ready(function(){
    $("tr.best_articles_table_content").hover(
        function(event) {
            $(this).addClass("highlight");
        },
        function(event) {
            $(this).removeClass("highlight");
        }
    );
    $("tr.best_articles_table_content").click(
        function(event) {
            $.post("/", {aaa: "asdf"},
                function(data, textStatus) {
                    alert(data);
                }
            );
        }
    );
});
