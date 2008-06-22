# -*- coding: utf-8 -*-

class ArticleManager(object):
    """
    게시글 및 검색 처리 클래스
    """

    def __init__(self):
        pass

    def read(self, session_key, no, board_name):
        """
        DB로부터 게시글 하나를 읽어옴

        >>> article.read(session_key, 300, "garbages")
	True, {"no": 32, "read_status":N, "title": "성진이는 북극곰", ....}

	    - Current Article Dictionary { no, read_status, title, author, date, hit, vote }

        @type  session_key: string
        @param session_key: User Key
        @type  no: number
        @param no: Article Number
        @type board_name: string
        @param board_name : BBS Name
        @rtype: dictionary
        @return:
            1. Read 성공: True, Article Dictionary
            2. Read 실패:
		1. 존재하지 않는 게시물번호: False, {"ARTICLE_NOT_EXIST"}
		2. 존재하지 않는 게시판: False, {"BOARD_NOT_EXIST"}
		3. 로그인되지 않은 유저: False, {"NOT_LOGGEDIN"}
		4. 데이터베이스 오류: False, {"DATABASE_ERROR"}
        """

    def write(self, session_key, article_dic, board_name):
        """
        DB에 게시글 하나를 작성함

        >>> article.write(session_key, article_dic, "garbages")
	True, "32"

        @type  session_key: string
        @param session_key: User Key
        @type  article_dic: dictionary
        @param article_dic: Article Dictionary
        @type board_name: string
        @param board_name : BBS Name
        @rtype: string
        @return:
            1. Write 성공: True, Article Number
            2. Write 실패:
		1. 존재하지 않는 게시판: False, "BOARD_NOT_EXIST"
		2. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		3. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def modify(self,session_key, no, article_dic, board_name):
        """
        DB의 해당하는 게시글 수정

        >>> article.modify(session_key, 300, article_dic, "garbages")
	True, "32"

        @type  session_key: string
        @param session_key: User Key
        @type  no: integer
        @param no: Article Number
        @type  article_dic : dictionary
        @param article_dic : Article Dictionary
        @type board_name: string
        @param board_name : BBS Name
        @rtype: string
        @return:
            1. Modify 성공: True, Article Number
            2. Modify 실패:
		1. 존재하지 않는 게시물번호: False, "ARTICLE_NOT_EXIST"
		2. 존재하지 않는 게시판: False, "BOARD_NOT_EXIST"
		3. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		4. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def delete(self, session_key, no, board_name):
        """
        DB에 해당하는 글 삭제

        >>> article.delete(session_key, 300, "garbages")
	True, "OK"
        
        @type  session_key: string
        @param session_key: User Key
        @type  no: number
        @param no: Article Number
        @type board_name: string
        @param board_name : BBS Name
        @rtype: string 
        @return:
            1. Delete 성공: True, "OK"
	    2. Delete 실패:
		1. 존재하지 않는 게시물번호: False, "ARTICLE_NOT_EXIST"
		2. 존재하지 않는 게시판: False, "BOARD_NOT_EXIST"
		3. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		4. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def article_list(self, session_key, board_name, page=1, page_length=20):
        """
        게시판의 게시글 목록 읽어오기

        >>> article.article_list(session_key, "garbages", 2, 18)
	True, [{"no": 1, "read_status": "N", "title": ...}, {"no": 2, "read_status": "R", "title": ...}, ...]

        @type  session_key: string
        @param session_key: User Key
        @type board_name: string
        @param board_name : BBS Name
        @type  page: integer
        @param page: Page Number to Request
        @type  page_length: integer
        @param page_length: Count of Article on a Page
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: True, Article List
	    2. 리스트 읽어오기 실패:
		1. 존재하지 않는 게시판: False, "BOARD_NOT_EXIST"
		2. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		3. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def board_list(self, session_key):
        """
        게시판 목록 읽어오기

        >>> article.board_list(session_key)
	True, ["garbages", "love", "buynsell[com]", ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: True, Board List
            2. 리스트 읽어오기 실패: False
		1. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		2. 데이터베이스 오류: False, "DATABASE_ERROR"
        """

    def search(self, session_key, board_name, query_text, search_type, page=1, page_length=20):
        """
        게시물 검색

        >>> article.search(session_key, "garbages", "심영준바보", "All", 2, 18)
	True, [{"no": 1, "read_status": "N", "title": ...}, {"no": 2, "read_status": "R", "title": ...}, ...]

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: BBS Name
        @type  query_text: string
        @param query_text: Text to Search
        @type  search_type: string
        @param search_type: Search Type (Title, Context, Author, Date, All)
        @type  page: integer
        @param page: Page Number to Request
        @type  page_length: integer
        @param page_length: Count of Article on a Page
        @rtype: list
        @return:
            1. 검색 성공: True, Article List
	    2. 검색 실패:
		1. 검색 결과가 존재하지 않음: False, "NOT_FOUND"
		2. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		3. 데이터베이스 오류: False, "DATABASE_ERROR"

        """

