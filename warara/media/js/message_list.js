$(document).ready(function() {
	$("input[name='ch_del_enm']").click(function() {
		$("input[name='flag_del_enm']").val() = 0;
		var checked = this.checked;
		$("input.ch_del_d").each(function(){
			this.checked = checked;
			});
	});
})
