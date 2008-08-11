$(document).ready(function(){
    $("dl.best_articles_table_content").hover(
        function(event) {
            $(this).addClass("highlight");
        },
        function(event) {
            $(this).removeClass("highlight");
        }
    );
    $("dl.best_articles_table_content").click(
        function(event) {
            /*$.post("/", {aaa: "asdf"},
                function(data, textStatus) {
                    alert(data);
                }
            );*/
        }
    );

	$(document).keypress(function(event){
		switch(event.which){
		case 113: //q
		location.href = "/account/logout";
		break;
		}
		});
});
