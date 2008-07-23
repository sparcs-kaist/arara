$(document).ready(function(){
    $(".radio").click(function(event) {
        if ($("#disagree:checked").val()) {
            $("#disagree").parent().children("label").children("span.feedback")
                .text("Want you create an account, you should check Agree");
        }
        else
            $("#disagree").parent().children("label").children("span.feedback").text("");
    });
    
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
    
    $("#register_submit").click(function(event) {
        $("input.required_field").each(function(i) {
            if (!$(this).val()) {
                $(this).parent().children("label").children("span.feedback")
                    .text("The field is empty");
                event.preventDefault();
            }
        }); 
        if (!($("#password_field").val() == $("#re_password_field").val())) {
            $("#password_field").parent().children("label").children("span.feedback")
                .text("The password doesn't matched with the re-enter");
            event.preventDefault();
        }
        if ($("#disagree:checked").val()) {
            $("#disagree").parent().children("label").children("span.feedback")
                .text("Want you create an account, you should check Agree");
            event.preventDefault();
        }
        alert("Please confirm your form");
    });
});
