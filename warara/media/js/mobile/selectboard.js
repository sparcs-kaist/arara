function jq(id) {
    return '#' + id.replace(/([ #;&,.+*~\':"!^$[\]()=>|\/@])/g,'\\$1');
}

$(document).ready(function(){
    $(".fav").click(function(event){
        var box = $("#contentWrap").next();
        if(box.hasClass('dash')){
            box.removeClass('dash').addClass('nodash');
            var qa = [];
            $(".icona.selected, .no_icona.selected").each(function(){
                qa.push($(this).children('.tt').attr('id'));
                $(this).removeClass('selected');
            });
            $("#boards").val(qa.join("/"));
            $("#save_form").submit();
        }
        else {
            box.removeClass('nodash').addClass('dash');
            var qs = $("#boards").val();
            if(qs != ""){
                qarr = qs.split('/');
                for(var i in qarr)
                    $(jq(qarr[i])).parent().addClass('selected');
            }
        }
        event.preventDefault();
    });

    function toggle_board(event) {
        if($("#contentWrap").next().hasClass('dash')){
            if(!$(this).hasClass('selected') && $(".icona.selected, .no_icona.selected").length >= 3) alert("You can choose at most 3 boards.");
            else $(this).toggleClass('selected');
            event.preventDefault();
        }
        else return true;
    }
    $(".no_icona").click(toggle_board);
    $(".icona").click(toggle_board);

});
