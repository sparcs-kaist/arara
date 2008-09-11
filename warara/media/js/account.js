$(document).ready(function(){
    if ($("#contempo_acc_admin").children("a").attr("rel") == "account_modify") {$("#mynickname").focus();} 
    else if ($("#contempo_acc_admin").children("a").attr("rel") == "password_modify") {$("#last_password_field").focus();}
    else {$("#id").focus();}

    var id;
    var nickname;
    var email;
    
    $("input.required_field").focus(function() {
        $(this).parent().children("label").children("span.feedback").text("");
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
        $("#id").keydown(function(event) {
            id = $("#id").val(); 
            if(event.keyCode == 09) {
                $.post("/account/register/idcheck/", {check_field: id},
                    function(data, textStatus) {
                        $("#id").parent().children("label").children("span.feedback").text(data);
                    }
                );
            }
        });
        $("#nickname").keydown(function(event) {
            nickname = $("#nickname").val();
            if(event.keyCode == 09) {
                $.post("/account/register/nicknamecheck/", {check_field: nickname},
                    function(data, textStatus) {
                        $("#nickname").parent().children("label").children("span.feedback").text(data);
                    }
                );
            }
        });
        $("#email").keydown(function(event) {
            email = $("#email").val();
            if(event.keyCode == 09) {
                if ((document.form.email.value.indrxOf('@') == -1 ) || (document.form.email.value.indexOf('.') == -1)) {
                    $("#email").parent().children("label").children("span.feedback").text("The e-mail form is not proper");
                }
                else {
                    $.post("/account/register/emailcheck/", {check_email_field: email},
                        function(data, textStatus) {
                            $("#email").parent().children("label").children("span.feedback").text(data);
                        }
                    );
                }
            }
        });
    }); 

    $(".submit").click(function(event) {
        $("input.required_field").each(function(i) {
            if (!$(this).val()) {
                $(this).parent().children("label").children("span.feedback")
                    .text("The field is empty");
                $(".submit").parent().parent().children("label").children("span.feedback").text("Please confirm your form");
                event.preventDefault();
            }
        });
        if (!($("#password_field").val() == $("#re_password_field").val())) {
            $("#password_field").parent().children("label").children("span.feedback")
                .text("The password doesn't matched with the re-enter");
            $(".submit").parent().parent().children("label").children("span.feedback").text("Please confirm your form");
            event.preventDefault();
        }
        if ((document.form.email.value.indexOf('@') == -1 ) || (document.form.email.value.indexOf('.') == -1)) {
            $("#email").parent().children("label").children("span.feedback").text("The e-mail form is not proper");
            $(".submit").parent().parent().children("label").children("span.feedback").text("Please confirm your form");
            event.preventDefault();
        }
    });

    //shortcut

    $cursor_atm = 0;
    $select_atm = ".account_head_block a";
    $length_atm = $($select_atm).length;
    $($select_atm).eq(0).addClass("hidden_highlight");

    $update_focus = function(ex_div, cursor){
        $(ex_div + ".row_highlight").removeClass("row_highlight");
        $(ex_div).eq(cursor).addClass("row_highlight");
    }

    $move_next = function(ex_div, cursor, length){
        if(cursor < length-1){
            cursor++;
        }
        return cursor;
    }

    $move_prev = function(ex_div, cursor, length){
        if(cursor > 0){
            cursor--;
        }
        return cursor;
    }
    $(document).keypress(function(event){
            if($focus_input){
            return;
            }
            if(event.altKey || event.ctrlKey){
            return;
            }
            if($($select_atm + ".row_highlight").length){
                switch(event.which){
                    case 106:
                        $cursor_atm = $move_prev($select_atm, $cursor_atm, $length_atm);
                        $update_focus($select_atm, $cursor_atm);
                        break;
                    case 107:
                        $cursor_atm = $move_next($select_atm, $cursor_atm, $length_atm);
                        $update_focus($select_atm, $cursor_atm);
                        break;
                    case 32:
                        location = $($select_atm).eq($cursor_atm).attr("href");
                        event.preventDefault();
                        break;
                    } 
            }
            switch(event.which){
                case 115:
                    $update_focus($select_atm, $cursor_atm);
                    break;
            }
            });
});
