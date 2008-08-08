$(document).ready(function() {

		$("input[name='file_input_delete']").click(function(){
			$(this).parent().remove();
			});
		$file_no = 1;
			$file_no++;
			$file_input_append = "<p name=" + $file_no + ">\n<caption>file " + $file_no + " : </caption>\n<input type=\"file\" name=\"file" + $file_no + "\"></input>\n<input type=\"button\" value=\"-\" name=\"file_input_delete\"></input>\n</p>";
			$("#article_write_file").append($file_input_append);
		$("input[name='file_input_add']").click(function(){
			$file_no++;
			$file_input_append = "<p name=" + $file_no + ">\n<caption>file " + $file_no + " : </caption>\n<input type=\"file\" name=\"file" + $file_no + "\"></input>\n<input type=\"button\" value=\"-\" name=\"file_input_delete\"></input>\n</p>";
			$("#article_write_file").append($file_input_append);
			});

		$("input[name='cancel']").click(function(){
			history.go(-1);
			});
		$("input[name='file_input_delete']").click(function(){
			$(this).parent().remove();
			});
		});

