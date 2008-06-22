# -*- coding: utf-8 -*-

class MessagingManager(object):
    """
    회원간 쪽지기능등을 담당하는 클래스
    """

    def __init__(self):
        pass

    def sent_list(self, session_key):
        """
        보낸 쪽지 리스트 읽어오기

        >>> messaging.sent_list(session_key)
	True, [{"id_who_sent": "pv457", "id_to_send": "serialx",
	"message_article": "야! 너 북극곰이라며?", "time_when_sent": "2008.02.13 12:13:43"}, ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: True, Message List
            2. 리스트 읽어오기 실패:
		1. 로그인되지 않은 사용자: False, "NOT_LOGGEDIN"
		2. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def receive_list(self, session_key):
        """
        받은 쪽지 리스트 읽어오기

        >>> messaging.receive_list(session_key)
	True, [{"id_who_sent": "serialx", "id_to_send": "pv457",
	"message_article": "장난? 아니거등?", "time_when_sent": "2008.02.13 12:15:32"}, ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: True, Message List
            2. 리스트 읽어오기 실패:
		1. 로그인되지 않은 사용자: False, "NOT_LOGGEDIN"
		2. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def send_message(self, session_key, id_to_send, msg_dic):
        """
        쪽지 전송하기

        >>> messaging.send_message(session_key, "pv457", msg_dic)
	True, "OK"

	--msg_dic: {id_who_sent, id_to_send, message_article, time_when_sent}

        @type  session_key: string
        @param session_key: User Key
        @type  id_to_send: string
        @param id_to_send: Destination ID
        @type  msg_dic: dictionary
        @param msg_dic: Message Dictionary
        @rtype: string
        @return:
            1. 메세지 전송 성공: True, "OK"
	    2. 메세지 전송 실패:
		1. 보낼 아이디가 존재하지 않음: False, "ID_TO_SEND_NOT_EXIST"
		2. 로그인되지 않은 사용자: False, "NOT_LOGGEDIN"
		3. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
