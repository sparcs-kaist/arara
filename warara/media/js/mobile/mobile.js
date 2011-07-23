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
