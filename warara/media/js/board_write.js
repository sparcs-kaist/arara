$(document).ready(function() {
        // 이제는 사용자가 몇 개의 파일을 올릴 수 있는지 예측하는 변수가 되었다.
        // 사용자는 file_no 이상의 파일을 올릴 리가 없다.
		$file_no = 1;

	$("input[name='file_input_add']").click(function(){
		$file_no++;
		$("#file_line_model .file_upload_t input[type='file']").remove();
		var file_append = "<input type=\"file\" name=\"file" + $file_no + "\" class=\"file_upload\" size=\"95\"></input>";
		$("#file_line_model .file_upload_t").append(file_append);
		$("#article_write_file").append($("#file_line_model").contents().clone());

		$("input[name='file_input_delete']").click(function(){
			$file_no--;
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

    $focus_input_title = 0;
    $focus_textarea_text = 0;
    $("#article_write_title input[name='title']").focus(function(){
            $focus_input_title = 1;
            });
    $("#article_write_title input[name='title']").blur(function(){
            $focus_input_title = 0;
            });
    $("#article_write_text textarea[name='text']").focus(function(){
            $focus_textarea_text = 1;
            });
    $("#article_write_text textarea[name='text']").blur(function(){
            $focus_textarea_text = 0;
            });
    $("#article_write_title input[name='title']").focus();
    
    $(document).keypress(function(event){
        if((event.shiftKey && $focus_textarea_text) || $focus_input_title){
        switch(event.which){
            case 13:
                if(confirm("send")){
                    $("form[name='article_write']").submit();
                    break;
                }
                event.preventDefault();
            }
            }
		if($focus_input || event.altKey || event.ctrlKey){
		return;
		}
        switch(event.which){
            case 113:
                location.href = "../";
                break;
                }
    });

    $("#write_button").click(function(event) {
        if ( $("input[name='board_type']").val() == 1 )
        {
            $file_uploaded = false;

            for ( $i=1 ; $i<=$file_no ; $i++ )
            {
                $upload_file_name = $("input[name='file" + $i + "']").val().split('.');
                $file_extension = $upload_file_name[$upload_file_name.length-1].toLowerCase();
                // 파일 이름이 없거나 있어도 그림 파일 확장자가 아니면 file_uploaded가 false다
                if ( $file_extension != "" )
                    if ( $file_extension != "jpg" && $file_extension != "gif" && $file_extension != "png" && $file_extension != "bmp" )
                    {
                        alert("Upload picture file only. ex) jpg, gif, png, bmp");

                        return false;
                    }
                    else
                        $file_uploaded = true;
            }

            // file_uploaded가 false면 제대로 파일을 올리지 않은 것이므로 경고.
            if ( !$file_uploaded )
            {
                alert("Upload at least one picture file.");

                return false;
            }
        }
        
        $("#article_write").submit();
        $("#write_button").attr("disabled", "disabled");
    });
});
