$(document).ready(function(){
    var read_anchors = document.getElementsByName('message_read_anchor');
    for(var i=0; i<read_anchors.length; i++){
        read_anchors[i].onclick = function(){
            read_message.msg_no.value = this.value;
            read_message.submit();
        }
    }
})
