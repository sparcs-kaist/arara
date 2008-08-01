$(document).ready(function() {
	$("input[name='ch_del_enm']").click(function() {
		var checked = this.checked;
		$("input.ch_del_d").each(function(){
			this.checked = checked;
			});
	});
})
