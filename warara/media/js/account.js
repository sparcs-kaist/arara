$(document).ready(function(){
    $("input.required_field").keyup(function(event) {
        if (!$(this).val()) {
            $(this).parent().children("label").children("span.feedback")
                .text("The field is empty");
        }
        else
            $(this).parent().children("label").children("span.feedback").text("");
    });

    $("#re_password_field").keyup(function(event) {
        if (!($("#password_field").val() == $("#re_password_field").val())) {
            $("#password_field").parent().children("label").children("span.feedback")
                .text("The password doesn't matched with the re-enter");
        }
        else
            $("#password_field").parent().children("label").children("span.feedback").text("");
    });
    
    $(".submit").click(function(event) {
        $("input.required_field").each(function(i) {
            if (!$(this).val()) {
                $(this).parent().children("label").children("span.feedback")
                    .text("The field is empty");
                $("#register_submit").parent().children("label").children("span.feedback").text("Please confirm your form");
                event.preventDefault();
            }
        }); 
        if (!($("#password_field").val() == $("#re_password_field").val())) {
            $("#password_field").parent().children("label").children("span.feedback")
                .text("The password doesn't matched with the re-enter");
            $("#register_submit").parent().children("label").children("span.feedback").text("Please confirm your form");
            event.preventDefault();
        }
    });
});
