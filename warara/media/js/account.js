$(document).ready(function(){
    if ($("#contempo_acc_admin").children("a").attr("rel") == "account_modify") {$("#mynickname").focus();} 
    else if ($("#contempo_acc_admin").children("a").attr("rel") == "password_modify") {$("#last_password_field").focus();}
    else {$("#id").focus();}

    var id;
    var nickname;
    var email;
    
    $("input.required_field").focus(function() {
        $(this).parent().children("label").children("span.feedback").text("");
        $("input.required_field").blur(function(event) {
            if (!$(this).val()) {
                $(this).parent().children("label").children("span.feedback").text("The field is empty");
            }
            else {
                $(this).parent().children("label").children("span.feedback").text("");
            }
        });
        $("#re_password_field").keyup(function(event) {
            if (!($("#password_field").val() == $("#re_password_field").val())) {
                $("#password_field").parent().children("label").children("span.feedback")
                    .text("The password are not matched with the re-entered");
                $textPasswordTest = 1;
            }
            else {
                $("#password_field").parent().children("label").children("span.feedback").text("");
                $textPasswordTest = 0;
            }
        });
        $("#id").blur(function(event) {
            id = $("#id").val(); 
            if (document.form.id.value.indexOf(' ') >= 0) {
                $("#id").parent().children("label").children("span.feedback").text("White space in ID is not allowed");
            }
            else {
                if (id != "") {
                    $.post("/account/register/idcheck/", {check_field: id},
                        function(data, textStatus) {
                            $idDupleTest = data;
                            if ($idDupleTest == 1)
                                {$("#id").parent().children("label").children("span.feedback").text("The ID is not available");}
                            else 
                                {$("#id").parent().children("label").children("span.feedback").text("");}
                        });
                }
            }
        });
        $("#nickname").blur(function(event) {
            nickname = $("#nickname").val();
            if (nickname != "") {
                $.post("/account/register/nicknamecheck/", {check_field: nickname},
                    function(data, textStatus) {
                        $nickDupleTest = data;
                        if ($nickDupleTest == 1)
                            {$("#nickname").parent().children("label").children("span.feedback").text("The nickname is not available");}
                        else 
                            {$("#nickname").parent().children("label").children("span.feedback").text("");}
                    }
                );
            }
        });
        $("#email").blur(function(event) {
            email = $("#email").val();
            if (email != "") {
                if ((document.form.email.value.indexOf('@') == -1 ) || (document.form.email.value.indexOf('.') == -1)) {
                    $("#email").parent().children("label").children("span.feedback").text("The e-mail form is not proper");
                }
                else {
                    $.post("/account/register/emailcheck/", {check_email_field: email},
                        function(data, textStatus) {
                            $emailDupleTest = data;
                            if ($emailDupleTest == 1)
                                {$("#email").parent().children("label").children("span.feedback").text("The email is not available");}
                            else 
                                {$("#email").parent().children("label").children("span.feedback").text("");}
                        }
                    );
                }
            }
        });
    }); 
    //alert if there exists the same nickname as entered nickname
        $("#register_submit input[name='done']").click(function(event){
            var nickname = $("#mynickname").val();
            if (nickname == $("#mynickname").attr("rel")){
            return;
            }
            $.post("/account/register/nickname" + "check/", 
                {check_field:nickname, from_message_send:1}, 
                function(data){
                if(data == 1){
                    alert("nickname " + nickname + " is already exist");
                }
                else{
                    $("#account_information_content").submit();
                }
                });
            event.preventDefault();
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
        if (document.form.id.value.indexOf(' ') >= 0) {
            $("#id").parent().children("label").children("span.feedback").text("White space in ID is not allowed");
            $(".submit").parent().parent().children("label").children("span.feedback").text("Please confirm your form");
            event.preventDefault();
        }
        if ($idDupleTest == 1 || $nickDupleTest == 1 || $emailDupleTest == 1) {
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
