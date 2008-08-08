$(document).ready(function() {
	$("input[name='ch_del_enm']").click(function() {
		$("input[name='flag_del_enm']").val() = 0;
		var checked = this.checked;
		$("input.ch_del_d").each(function(){
			this.checked = checked;
			});
	});

	$page_length = $("select[name='page_length'] option:selected").val();

	$("select[name='page_length']").change(function() {
		$("select[name='page_length'] option:selected").each(function(){
			$src = "/message/" + $("input[name='message_list_type']").val() + "?page_no=" + $("input[name='page_no']").val() + "&page_length=" + $(this).val();
			location.href = $src;
			});
		});

	var cursor_pos = 1;
	var row_length = $("#message_list_table tbody tr").length;
	$page_no = $("input[name='page_no']").val();
	$last_page = $("input[name='last_page']").val();

	$.history.init(function(hash){
		if(hash){
		alert(parseint(hash));
		}
		});

	function read_message(cursor_pos){
		$src = $("#message_list_table tr").eq(cursor_pos).children("td[name='text']").children("a").attr("href");
		location.href = $src;
	}

	function update_table(cursor_pos){
		$("#message_list_table tr").removeClass("row_highlight");
		$("#message_list_table tr").eq(cursor_pos).addClass("row_highlight");
	}

	function move_next(){
		if(cursor_pos < row_length){
			cursor_pos++;
			update_table(cursor_pos);
			}
		else if(cursor_pos == row_length){
			if($page_no < $last_page){
				$page_no++;
				$src = "/message/" + $("input[name='message_list_type']").val() + "?page_no=" + $page_no + "&page_length=" + $page_length;
				location.href = $src;
				}
			}
	}

	function move_prev(){
		if(cursor_pos > 1){
			cursor_pos--;
			update_table(cursor_pos);
			}
		else if(cursor_pos == 1){
			if($page_no > 1){
				$page_no--;
				$src = "/message/" + $("input[name='message_list_type']").val() + "?page_no=" + $page_no + "&page_length=" + $page_length;
				location.href = $src;
			}
		}
	}

	update_table(cursor_pos);

	$(document).keypress(function(event){
			switch(event.which){
			case 13:
			case 32:
				read_message(cursor_pos);
				break;

			case 106:
				move_next();
				break;

			case 107:
				move_prev();
				break;

			}
	});
});
