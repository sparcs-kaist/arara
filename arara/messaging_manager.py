# -*- coding: utf-8 -*-

class MessagingManager(object):
    """
    회원간 쪽지기능, 쿼리등을 담당하는 클래스
    """

    def __init__(self):
        pass

    def list(session_key):
        """
        쪽지 리스트 읽어오기

        >>> messaging.list(key)

        @type  session_key: string
        @param session_key: User Key
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: Message List
            2. 리스트 읽어오기 실패: False
        """

    def sendmsg(session_key, id_to_send, msg_dic):
        """
        쪽지 전송하기

        >>> messaging.sendmsg(session_key, "pv457", msg_dic)

        @type  session_key: string
        @param session_key: User Key
        @type  id_to_send: string
        @param id_to_send: Destination ID
        @type  msg_dic: dictionary
        @param msg_dic: Message Dictionary
        @rtype: boolean
        @return:
            1. 메세지 전송 성공: True
            2. 메세지 전송 실패: False
        """

    def query(session_key, query_id):
	"""
	쿼리 함수

	>>> messaging.query(session_key, "pv457")

	@type  session_key: string
	@param session_key: User Key
	@type  query_id: string
	@param query_id: User ID to send Query
	@rtype: dictionary
	@return:
	    1. 쿼리 성공: query_dic
	    2. 쿼리 실패: False

	    query_dic { self_introduce, user_ip }
