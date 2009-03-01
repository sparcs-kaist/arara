$(document).ready(function(){
    $("#username_text").focus();

    $(document).keypress(function(event){
        switch(event.which){
        case 47:
        location.href="/main";
        break;
        }
        });
});
