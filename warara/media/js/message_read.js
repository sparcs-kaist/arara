$(document).ready(function(){
		$(document).keypress(function(event){
			if($focus_input || event.altKey || event.ctrlKey){
			return;
			}
			switch(event.which){

			case 113: //q
			$src = $("a[name='message_read_move_to_list']").attr("href");
			location.href = $src;
			break;

			case 114: //r
			case 109: //m
			if($("input[name='message_list_type']").val() == 'outbox'){
			return;
			}
			$("#message_send_text textarea").focus();	
			break;

			case 100: //d
			$src = $("a[name='message_read_delete']").attr("href");
			location.href = $src;
			break;
			}
			});
		});
