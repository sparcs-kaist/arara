$(document).ready(function() {
		$file_no = 1;

	$("input[name='file_input_add']").click(function(){
		$file_no++;
		$("#file_line_model span.article_write_file_caption").text("file " + $file_no);
		$("#file_line_model input.file_upload").attr("name", "file"+$file_no);
		$("#article_write_file").append($("#file_line_model").contents().clone());

		$("input[name='file_input_delete']").click(function(){
			$(this).parent().parent().remove();
			});

		$("input.file_upload").change(function(){
			$(this).parent().parent().children("div.file_upload_f").children("input.file_input_f").val($(this).val());
			});
		});

	$("input[name='cancel']").click(function(){
		history.go(-1);
		});

	$("input.file_upload").change(function(){
		$(this).parent().parent().children("div.file_upload_f").children("input.file_input_f").val($(this).val());
		});

	$("a.delete_file_button").click(function(){
			var article_id = $("input[name='article_no']").val();
			var board_name = $("input[name='board_name']").val();
			var file_id = $(this).parent().children("input[name='file_id']").val();
			var delete_url = "/board/" + board_name + "/delete_file";
			$.get(delete_url, {'article_id':article_id, 'file_id':file_id}, function(data){
				alert(data);
				$(this).parent().remove();
				});
			});

	});

