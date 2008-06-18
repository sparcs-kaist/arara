# -*- coding: utf-8 -*-

class ReadStatusManager(object):

    def __init__(self):
        pass

    def checkstat(session_key, bbs_name, no):
        """
        읽은 글인지의 여부를 체크

        @type  session_key: string
        @param session_key: User Key
        @type  bbs_name: string
        @param bbs_name: BBS Name
        @type  no: integer
        @param no: Article Number
        @rtype: boolean
        @return:
            1. 이미 읽은 글: True
            2. 읽지 않은 글: False
        """

    def add(session_key, bbs_name, no):
        """
        읽은 글로 등록하기

        @type  session_key: string
        @param session_key: User Key
        @type  bbs_name: string
        @param bbs_name: BBS Name
        @type  no : integer
        @param no : Article Number
        @rtype: boolean
        @return:
            1. 등록 성공: True
            2. 등록 실패: False
        """
