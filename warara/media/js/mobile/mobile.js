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
        url = $(this).attr('href');
        $.get(url, function(data){
            if(data == "OK") alert("Successfully voted");
            else if(data == "ALREADY_VOTED") alert("You voted already");
            else alert("Unknown error");
        });
        event.preventDefault();
    });

    // 글 쓰기/수정 모드에서 취소를 눌렀을 때 바로 전으로 이동
    $(".write_buttons .left input").click(function(event){
        history.go(-1);
        event.preventDefault();
    });
});
