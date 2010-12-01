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
            alert('로그아웃 되었습니다');
            location.reload();
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
