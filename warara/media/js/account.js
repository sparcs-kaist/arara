$(document).ready(function(){
    $("#id").focus();
    var id;
    var nickname;
    
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
        $("#id").keydown(function(event) {
            id = $("#id").val(); 
            if(event.keyCode == 09) {
                $.post("/account/register/idcheck/", {check_id_field: id},
                    function(data) {
                        $("#id").parent().children("label").children("span.feedback").text(data);
                    }
                );
            }
        });
        $("#nickname").keydown(function(event) {
            nickname = $("#nickname").val();
            if(event.keyCode == 09) {
                $.post("/account/register/nicknamecheck/", {check_nickname_field: nickname},
                    function(data) {
                        $("#nickname").parent().children("label").children("span.feedback").text(data);
                    }
                );
            }
        });
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
});
