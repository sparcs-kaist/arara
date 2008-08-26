$(document).ready(function(){
        $("#message_send_buttons input[name='submit']").click(function(event){
            var receiver = $("input[name='receiver']").val();
            var receiver_type = $("input[name='receiver_type']").val();
            $.post("/account/register/" + receiver_type + "check/", 
                {check_field:receiver, from_message_send:1}, 
                function(data){
                if(data == 1){
                    document.message_send.submit();
                }
                else{
                    alert(receiver + "is not exist");
                }
                });
            event.preventDefault();
        });

        $("a[name='select_receiver_type']").click(function(event){
            $("span.select_type").toggle();
            event.preventDefault();
            $("input[name='receiver_type']").val($("a[name='select_receiver_type'] span:visible").attr("rel"));
        });
 });
