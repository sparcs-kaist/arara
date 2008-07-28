$(document).ready(function(){
	$("a[name='message_page_move']").click(function(event) {
		$url = "/message/" + $("#message_list_type").val()
		$.get(url, {msg_no: this.val()});
		event.preventDefalult();
	});
})
