$(document).ready(function() {
		$file_no = 1;

	$("input[name='file_input_add']").click(function(){
		$file_no++;
		$("#file_line_model span.article_write_file_caption").text("file " + $file_no);
		$("#file_line_model .file_upload_t input[type='file']").remove();
		var file_append = "<input type=\"file\" name=\"file" + $file_no + "\" class=\"file_upload\" size=\"95\"></input>";
		$("#file_line_model .file_upload_t").append(file_append);
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

	$("a.delete_file_button").click(function(event){
			$file_anchor = $(this).parent().children("a[name='file_name']");
			$file_anchor.toggleClass("deleted_file");
			event.preventDefault();
			});

	$("input[name='article_write']").click(function(event){
			$("a.deleted_file").each(function(){
				$file_anchor = $(this);
				$("input[name='delete_file']").val($("input[name='delete_file']").val() + "&" + $file_anchor.attr("rel"));
				});
			});
	});

