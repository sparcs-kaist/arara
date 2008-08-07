$(document).ready(function() {
	$("input[name='ch_del_enm']").click(function() {
		$("input[name='flag_del_enm']").val() = 0;
		var checked = this.checked;
		$("input.ch_del_d").each(function(){
			this.checked = checked;
			});
	});

	$("select[name='page_length']").change(function() {
		$("select[name='page_length'] option:selected").each(function(){
			$src = "/message/" + $("input[name='message_list_type']").val() + "?page_no=" + $("input[name='page_no']").val() + "&page_length=" + $(this).val();
			location.href = $src;
			});
		});
})
