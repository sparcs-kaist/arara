# -*- coding: utf-8 -*-

class LoggingManager(object):
    """
    로깅관련 함수들을 모아놓은 클래스
    아직 초안이라 논의되지 않은 메소드가 많음. 개선 필요
    """

    def __init__(self):
	pass

    def search(self, session_key, log_search_dic):
	"""
	로그 테이블을 검색하는 함수

	>>> logging.search(session_key, log_search_dic)

	  - Current log_search_dic { board_name, article_no, user_id, title, author, date }
	    NULL Values are allowed for each key.

	@type  session_key: string
	@param session_key: User Key
	@type  log_search_dic: dictionary
	@param log_search_dic: Log Search Query Dictionary
	@rtype: list
	@return:
	    1. 검색 성공: Log Dictionary List
	    2. 검색 실패: False
	"""
