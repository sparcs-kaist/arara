# -*- coding: utf-8 -*-

class MessagingManager(object):

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

        >>> sendmsg(session_key, "pv457", msg_dic)

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
