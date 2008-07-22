$(document).ready(function(){
    $(".delete_user").click(function(event) {
        $("#blacklist_delete_form #username").attr("value", this.name);
        $("#blacklist_delete_form").submit();
    });
});
