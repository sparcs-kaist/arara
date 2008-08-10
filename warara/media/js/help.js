$(document).ready(function(){
		$("#help_content").append($("#help_base").contents().clone());

		$("#help_top_menu a").click(function(event){
			$help = $(this).attr("href").split('/')[2];
			$("#help_content").contents().remove();
			$("#help_content").append($("#help_" + $help).contents().clone());
            if(event.preventDefault){
			    event.preventDefault();
            }
            else{
                event.returnValue = false;
            }
			});
        });
