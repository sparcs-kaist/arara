$(document).ready(function(){
        var cursor = 0;
        var ht_length = $("#help_top_menu a").length;

        update_highlight();
        update_content("base");

		$("#help_top_menu a").click(function(event){
			$content_title = $(this).attr("href").split('/')[2];
            update_content($content_title);
            event.preventDefault();
			});

        function move_next(){
            if(cursor< ht_length-1){
            cursor ++;
            }
            update_highlight();
        }

        function move_prev(){
            if(cursor>0){
                cursor --;
            }
            update_highlight();
        }

        function update_highlight(){
            $(".row_highlight").removeClass("row_highlight");
            $("#help_top_menu a").eq(cursor).addClass("row_highlight");
        }

        function update_content($help){
            $(".selected").removeClass("selected");
            $("#help_top_menu a[rel='" + $help + "']").addClass("selected");
			$("#help_content").contents().remove();
			$("#help_content").append($("#help_" + $help).contents().clone());
        }

        $(document).keypress(function(event){
			if(!$("#help_top_menu a.row_highlight").length){
			return;
			}
			if($focus_input || event.ctrlKey || event.altKey){
			return;
			}

            switch(event.which){
                case 106:
                    move_prev();
                    break;

                case 107:
                    move_next();
                    break;

                case 32:
                case 39:
                    $content_title = $("#help_top_menu a").eq(cursor).attr("rel");
                    update_content($content_title);
                    break;
            }
        });
});
