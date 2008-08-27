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

    function logout(){
			$.get("/account/logout", function(data){
                $("#top_menu a.hidden").removeClass("hidden");
				$("a[name='logout']").hide();
				$("a[name='login']").show();
				$("a[name='account']").hide();
				$("a[name='register']").show();
				$("a[name='top_menu_message']").hide();
				$("a[name='blacklist']").hide();
				});
    }

	$(document).keypress(function(event){
		if(!$logged_in || $focus_input || event.altKey || event.ctrlKey){
		return;
		}
		switch(event.which){
		case 113: //q
        $(".highlight").removeClass("highlight");
        cursor_tm = 0;
        logout();
		break;
		}
		});
});
