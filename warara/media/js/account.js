$(document).ready(function(){
    $("#id").focus();
    
    $("input.required_field").focus(function() {
        $("input.required_field").keyup(function(event) {
            if (!(event.keyCode == 09)) {
                if (!$(this).val()) {
                    $(this).parent().children("label").children("span.feedback").text("The field is empty");
                }
                else
                    $(this).parent().children("label").children("span.feedback").text("");
            }
        });
        $("#re_password_field").keyup(function(event) {
            if (!($("#password_field").val() == $("#re_password_field").val())) {
                $("#password_field").parent().children("label").children("span.feedback")
                    .text("The password doesn't matched with the re-enter");
            }
            else
                $("#password_field").parent().children("label").children("span.feedback").text("");
        });
        $("#email").keydown(function(event) {
            if(event.keyCode == 09) {
                if ((document.form.email.value.indexOf('@') == -1 ) || (document.form.email.value.indexOf('.') == -1)) {
                    $("#email").parent().children("label").children("span.feedback").text("The e-mail form is not proper");
                }
                else
                    $("#email").parent().children("label").children("span.feedback").text(""); 
            }
        });
        $(this).parent().children("label").children("span.feedback").text("");
    });
    
    $(".submit").click(function(event) {
        $("input.required_field").each(function(i) {
            if (!$(this).val()) {
                $(this).parent().children("label").children("span.feedback")
                    .text("The field is empty");
                $(".submit").parent().children("label").children("span.feedback").text("Please confirm your form");
                event.preventDefault();
            }
        });
        if (!($("#password_field").val() == $("#re_password_field").val())) {
            $("#password_field").parent().children("label").children("span.feedback")
                .text("The password doesn't matched with the re-enter");
            $(".submit").parent().children("label").children("span.feedback").text("Please confirm your form");
            event.preventDefault();
        }
        if ((document.form.email.value.indexOf('@') == -1 ) || (document.form.email.value.indexOf('.') == -1)) {
            $("#email").parent().children("label").children("span.feedback").text("The e-mail form is not proper");
            $(".submit").parent().children("label").children("span.feedback").text("Please confirm your form");
            event.preventDefault();
        }
    });

    $("#id_duplication_checking").click(function(event) {
        $.post("/account/register/idcheck/", {check_id_field: $("#check_id_field").val()},
            function(data, textStatus){
                alert(data);
                if (data == 'The ID is available') {
                    $("#id_check_popup").hide();
                }
            }
        );
        event.preventDefault();
    });

    $("#id_duplication_check").click(function(event) {
        $("#id_check_popup").show();
    });

    $("#nickname_duplication_checking").click(function(event) {
        $.post("/account/register/nicknamecheck/", {check_nickname_field: $("#check_nickname_field").val()},
            function(data, textStatus){
                alert(data);
                if (data == 'The nickname is available') {
                    $("#nickname_check_popup").hide();
                }
            }
        );
        event.preventDefault();
    });
    
    $("#nickname_duplication_check").click(function(event) {
        $("#nickname_check_popup").show();
    });
});
