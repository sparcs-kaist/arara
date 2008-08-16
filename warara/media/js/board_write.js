$(document).ready(function() {
		$file_no = 1;

	$("input[name='file_input_add']").click(function(){
		$file_no++;
		//$file_input_append = "<p name=" + $file_no + ">\n<caption>file " + $file_no + " : </caption>\n<input type=\"file\" name=\"file" + $file_no + "\"></input>\n<input type=\"button\" value=\"-\" name=\"file_input_delete\"></input>\n</p>";
		$("#file_line_model span.article_write_file_caption").text("file " + $file_no);
		$("#file_line_model input.file_upload").attr("name", "file"+$file_no);
		$("#article_write_file").append($("#file_line_model").contents().clone());

		$("input[name='file_input_delete']").click(function(){
			$(this).parent().parent().remove();
			});
		});

	$("input[name='cancel']").click(function(){
		history.go(-1);
		});

	$("input[name='file1']").change(function(){
		$("input[name='file1_fi']").val($(this).val());
		});

	});

