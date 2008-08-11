$(document).ready(function(){
		$.post(location.pathname,function(data){
			alert(data);
			window.close();
			});
		});
