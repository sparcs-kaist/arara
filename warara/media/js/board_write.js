$(document).ready(function() {
    $file_no = 1;

    function create_more_attach_form(this_select, event){
        $file_no++;

        var new_attach = this_select.parent().parent().clone();
        var new_attach_id = "writePost_attach_" + $file_no;
        
        new_attach.children("th").children("label").attr("for", new_attach_id).text("첨부");
        new_attach.children("td").children("input").attr("name", new_attach_id).attr("id", new_attach_id);
        new_attach.children("td").children("input").html(new_attach.children("td input").html()); //reset the input field
        new_attach.children("td").children("a").click(function(event){
            create_more_attach_form($(this), event);
        });

        this_select.parent().parent().after(new_attach);
        this_select.after(
            $('<a class="file_delete" href="#">삭제</a>').click(function(event){
                $(this).parent().parent().remove();
                event.preventDefault();
            })
        );

        this_select.remove();
        event.preventDefault();
    }
       
    $(".writeAttach #attach_more").click(function(event){
        create_more_attach_form($(this), event);
    });
	$("#writePostCancel").click(function(){
		history.go(-1);
		});

	$("a.deleteAttachLink").click(function(event){
			$file_anchor = $(this).parent().children("a[name='file_name']");
			$file_anchor.toggleClass("deleted_file");
                        $(this).parent().parent().hide()
			event.preventDefault();
			});

	$("#writePostSubmit").click(function(event){
			$("a.deleted_file").each(function(){
				$file_anchor = $(this);
				$("input[name='delete_file']").val($("input[name='delete_file']").val() + "&" + $file_anchor.attr("rel"));
				});
			});

    $focus_input_title = 0;
    $focus_textarea_text = 0;
    $("#writePost_title").focus(function(){
            $focus_input_title = 1;
            });
    $("#writePost_title").blur(function(){
            $focus_input_title = 0;
            });
    $("#writePost_contents").focus(function(){
            $focus_textarea_text = 1;
            });
    $("#writePost_contents").blur(function(){
            $focus_textarea_text = 0;
            });
    $("#writePost_title").focus();
    
    $(document).keypress(function(event){
        if((event.shiftKey && $focus_textarea_text) || $focus_input_title){
        switch(event.which){
            case 13:
                if(confirm("send")){
                    $("form[name='writePost']").submit();
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

    $("#writePostSubmit").click(function(event) {

/* XXX(hodduc) : 현재 이 부분의 동작을 보장하고 있지 않음
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
*/
        $("#writePost").submit();
        $("#writePostSubmit").attr("disabled", "disabled");
    });

    // dropbox의 value를 초기화함. 처음에는 select box의 값이 default value이다
    // 그 이후에는 dropbox에서 click event가 발생시 select box의 data를 연동해 같이 변경시키면 됨
    var selected_idx = $("select[name='heading']").children().index( $("select[name='heading'] option:selected") );
    $(".dropBox a.#selected").text($("select[name'heading'] option:selected").text());
    $(".dropBox ul li").click(function(){
        var idx = $(this).parent().children().index($(this));
        $("select[name='heading'] option:eq("+idx+")").attr("selected", "selected");
    });
});
