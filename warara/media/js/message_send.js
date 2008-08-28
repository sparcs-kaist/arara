$(document).ready(function(){
        $("#message_send_buttons input[name='message_submit']").click(function(event){
            var receiver = $("input[name='receiver']").val();
            var receiver_type = $("input[name='receiver_type']").val();
            $.post("/account/register/" + receiver_type + "check/", 
                {check_field:receiver, from_message_send:1}, 
                function(data){
                if(data == 1){
                    document.message_send.submit();
                }
                else{
                    alert(receiver + " is not exist");
                }
                });
            event.preventDefault();
        });

        $("a[name='select_receiver_type']").click(function(event){
            $("span.select_type").toggle();
            event.preventDefault();
            $("input[name='receiver_type']").val($("a[name='select_receiver_type'] span:visible").attr("rel"));
        });

        $("#send_receiver").focus();

        $(document).keypress(function(event){
                if(event.shiftKey){
                switch(event.which){
                    case 13:
                        if(confirm("send")){
                            $("form[name='message_send']").submit();
                            break;
                        }
                    }
                    }
                if($focus_input || event.altKey || event.ctrlKey){
                return;
                }
                switch(event.which){
                    case 99:
                        $("span.select_type").toggle();
                        $("input[name='receiver_type']").val($("a[name='select_receiver_type'] span:visible").attr("rel"));
                        break;
                    case 70:
                        $("#send_receiver").focus();
                        break;
                }
        });

 });
