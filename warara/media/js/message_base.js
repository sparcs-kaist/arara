$(document).ready(function(){
        $(document).keypress(function(event){
            if($focus_input || event.altKey || event.ctrlKey){
            return;
            }
            switch(event.which){
            case 117:
                location.href = $("#message_menu a[name='inbox']").attr("href");
                break;
            case 111:
                location.href = $("#message_menu a[name='outbox']").attr("href");
                break;
            case 115:
                location.href = $("#message_menu a[name='send']").attr("href");
                }
                });
        });
