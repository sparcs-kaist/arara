// Mobile Ara :: Javascript

// ----- Login
// 입력 창에 포커스가 왔을 때 배경 그림을 지워주는 함수
function clear_input(f){
    document.getElementById(f).style.background="#FFFFFF";
}
// 입력 창에서 포커스가 떠날 때 배경 그림을 복구해주는 함수
function set_input(f){
    var input = document.getElementById(f)
    if(input.value == ''){
        if(f == 'id') input.style.background = "url('/media/image/mobile/input_bg.gif') no-repeat left top";
        else input.style.background = "url('/media/image/mobile/input_bg.gif') no-repeat left bottom";
    }
}

$(document).ready(function(){
    // 글/답글의 추천 버튼이 클릭되었을 때의 핸들러.
    // AJAX로 요청을 처리한 후 반환함
    $(".rec").click(function(event){
        var answer = confirm("Do you want to vote?")
        if (answer){
            url = $(this).attr('href');
            $.get(url, function(data){
                if(data == "OK") alert("Successfully voted");
                else if(data == "ALREADY_VOTED") alert("You voted already");
                else alert("Unknown error");
            });
        }
        event.preventDefault();
    });

    // 글 쓰기/수정 모드에서 취소를 눌렀을 때 바로 전으로 이동
    $(".write_buttons .left input").click(function(event){
        history.go(-1);
        event.preventDefault();
    });

    // 답글 달기 버튼 핸들러
    $(".add_reply").hide();
    function reply_handler(event) {
        // 만약 다른 곳에 있었던 답글 상자를 가져와야 한다면
        if($(this).parent().parent().parent().children(".add_reply").length == 0){
            var board_name = $(this).parent().parent().children("input.board_name").val();
            var article_id = $(this).parent().parent().children("input.article_id").val();
            var reply_url = "/mobile/board/" + board_name + "/" + article_id + "/reply/";

            p = $(".add_reply").hide().detach();
            if($(this).parent().parent().hasClass("re_info"))
                p = p.insertAfter($(this).parent().parent().next());
            else
                p = p.insertAfter($(this).parent().parent());

            p.toggle("fast");
            p.children().children("input[name='article_no']").val(article_id);
            p.children().attr('action', reply_url);
        }
        // 그렇지 않을 경우 toggle만
        else {
            $(".add_reply").toggle("fast");
        }
        $(".add_reply textarea").focus();
        event.preventDefault();
    }
    $('#article_buttons .reply').click(reply_handler);
    $('.re_info .reply').click(reply_handler);

    $('.box form').each(function(){
        var cookie = document.cookie;
        if(cookie.length > 0){
            start_ind = cookie.indexOf('saveID=');
            if(start_ind != -1){
                id = cookie.substring(start_ind + 7, cookie.length).split(';')[0];
                if(id.length > 0){
                    $('#saveID').attr('checked', 'checked');
                    $('#id').val(id);
                }
            }
            start_ind = cookie.indexOf('savePWD=');
            if(start_ind != -1){
                pw = cookie.substring(start_ind + 8, cookie.length).split(';')[0];
                if(pw.length > 0){
                    $('#savePWD').attr('checked', 'checked');
                    $('#pw').val(pw);
                }
            }
        }
    });

    $('.box form').submit(function(){
        var date = new Date(), expireDate = new Date();
        date.setTime(date.getTime() + 30*24*60*60*1000);
        expireDate.setTime(date.getTime() - 24*60*60*1000);
        if($('#saveID').is(':checked'))
            document.cookie = 'saveID' + '=' + $('#id').val() + "; expires=" + date.toGMTString();
        else
            document.cookie = 'saveID' + '=' + "; expires=" + expireDate.toGMTString();

        if($('#savePWD').is(':checked'))
            document.cookie = 'savePWD' + '=' + $('#pw').val() + "; expires=" + date.toGMTString();
        else 
            document.cookie = 'savePWD' + '=' + "; expires=" + expireDate.toGMTString();
    });

    $(".toggle_img").click(function(event){
        $(this).prev().append('<img src="' + $(this).attr('href') + '" class="attached_image" />');
        $(this).prev().show();
        $(this).hide();
        event.preventDefault();
    });
});
