# -*- coding: utf-8 -*-

class MemberManager(object):
    """
    회원 가입, 회원정보 수정, 이메일 인증등을 담당하는 클래스
    """

    def __init__(self):
        pass

    def register(user_reg_dic):
        """
        DB에 회원 정보 추가

        >>> member.register(user_reg_dic)

	    - Current User Dictionary { ID, password, nickname, email, sig, self_introduce, default_language }

        @type  user_reg_dic: dictionary
        @param user_reg_dic: User Dictionary
        @rtype: boolean
        @return:
            1. register 성공: True
            2. register 실패: False
        """

    def confirm(confirm_key):
        """
        인증코드 확인

        >>> member.confirm(confirm_session_key)

        @type  confirm_key: integer
        @param confirm_key: Confirm Key
        @rtype: boolean
        @return:
            1. 인증 성공: True
            2. 인증 실패: False
        """
        
    def modify(session_key, user_reg_dic):
        """
        DB에 회원 정보 수정

        >>> member.modify(session_key, user_reg_dic)

        @type  session_key: string
        @param session_key: User Key
        @type  user_reg_dic: dictionary
        @param user_reg_dic: User Dictionary
        @rtype: boolean
        @return:
            1. register 성공: True
            2. register 실패: False
        """


        
