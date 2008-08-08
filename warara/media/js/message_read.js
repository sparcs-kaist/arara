$(document).ready(function(){
		$(document).keypress(function(event){
			switch(event.which){

			case 113: //q
			$src = $("a[name='message_read_move_to_list']").attr("href");
			location.href = $src;
			break;

			case 114: //r
			case 109: //m
			$src = $("a[name='message_read_reply']").attr("href");
			location.href = $src;
			break;

			case 100: //d
			$src = $("a[name='message_read_delete']").attr("href");
			location.href = $src;
			break;
			}
			});
		});
