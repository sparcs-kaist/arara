#-*- coding: utf-8 -*-
'''
Password Modifier

ARAra 엔진에 직접 접근하여 사용자의 비밀번호를 교체해 준다.
'''

from arara_engine_connector import *

def modify_password(sysop_session_key, user_id, user_pw):
    get_server().member_manager.modify_password_sysop(sysop_session_key, UserPasswordInfo(username=user_id, new_password=user_pw))

def login(id, pw):
    return get_server().login_manager.login(id, pw, '127.0.0.1')

def logout(session_key):
    get_server().login_manager.logout(session_key)

def get_user_id(msg = ""):
    return raw_input("enter the %s id $" % msg)

def get_user_pw(msg = ""):
    return raw_input("enter the %s pw $" % msg)

def main():
    sysop_id = get_user_id("sysop")
    sysop_pw = get_user_pw("sysop")
    sysop_session_key = login(sysop_id, sysop_pw) # 로그인

    user_id = get_user_id("user")
    user_pw = get_user_pw("user")
    modify_password(sysop_session_key, user_id, user_pw) # 패스워드 변경
    logout(sysop_session_key)

    session_key = login(user_id, user_pw) # 로그인 테스트
    logout(session_key)

    print "done"

if __name__ == "__main__":
    main()
