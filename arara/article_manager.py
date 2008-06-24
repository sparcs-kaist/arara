# -*- coding: utf-8 -*-

class ArticleManager(object):
    """
    게시글 및 검색 처리 클래스
    현재 게시글 표시방식이 절묘하기 때문에 read 메소드에 관한 논의가 필요.
    
    article = {"garbages":{1:{"t":"2","b":"3"},2:{"t":"3","b":"4"}}}
    article["garbages"][1]
    """

    def __init__(self):
	self.articles = {'garbages': {} }

    def read(self, session_key, board_name, no):
        """
        DB로부터 게시글 하나를 읽어옴

        >>> article.read(session_key, "garbages", 300)
	True, {"no": 32, "read_status":N, "title": "성진이는 북극곰", ....}

	    - Current Article Dictionary { no, read_status, title, author, date, hit, vote }

        @type  session_key: string
        @param session_key: User Key
        @type  no: number
        @param no: Article Number
        @type board_name: string
        @param board_name : BBS Name
        @rtype: boolean, dictionary
        @return:
            1. Read 성공: True, Article Dictionary
            2. Read 실패:
		1. 존재하지 않는 게시물번호: False, "ARTICLE_NOT_EXIST"
		2. 존재하지 않는 게시판: False, "BOARD_NOT_EXIST"
		3. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		4. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
	try:
	    return self.articles[board_name][no]
	except KeyError:
	    return False, "BOARD_NOT_EXIST"
	except IndexError:
	    return False, "ARTICLE_NOT_EXIST"


    def write_article(self, session_key, board_name, article_dic):
        """
        DB에 게시글 하나를 작성함

        >>> article.write_article(session_key, "garbages",  article_dic)
	True, "32"

        @type  session_key: string
        @param session_key: User Key
        @type  article_dic: dictionary
        @param article_dic: Article Dictionary
        @type board_name: string
        @param board_name : BBS Name
        @rtype: boolean, string
        @return:
            1. Write 성공: True, Article Number
            2. Write 실패:
		1. 존재하지 않는 게시판: False, "BOARD_NOT_EXIST"
		2. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		3. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
	try:
	    self.articles[board_name].append(article_dic)
	    return True, "Article Number"
	except KeyError:
	    return False, "BOARD_NOT_EXIST"
	

    def write_reply(self, session_key, board_name, reply_dic, article_no):
	"""
	댓글 하나를 해당하는 글에 추가

	>>> article.write_reply(session_key,"garbages", reply_dic, 24)
	True, "24"

	@type  session_key: string
	@param session_key: User Key
	@type  reply_dic: dictionary
	@param reply_dic: Reply Dictionary
	@type  board_name: string
	@param board_name: BBS Name
	@type article_no: integer
	@param article_no: Article No in which the reply will be added
	@rtype: boolean, string
	@return:
	    1. 작성 성공: True, Article Number
	    2. 작성 실패:
		1. 존재하지 않는 게시판: False, "BOARD_NOT_EXIST"
		2. 존재하지 않는 게시물: False, "ARTICLE_NOT_EXIST"
		3. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		4. 데이터베이스 오류: False, "DATABASE_ERROR"
	"""
	try:
	    self.articles[board_name][article_no].append(reply_dic)
	except KeyError:
	    return False, "BOARD_NOT_EXIST"
	    return False, "ARTICLE_NOT_EXIST"



    def modify(self,session_key, board_name, no, article_dic):
        """
        DB의 해당하는 게시글 수정

        >>> article.modify(session_key, "garbages", 300, article_dic)
	True, "32"

        @type  session_key: string
        @param session_key: User Key
        @type  no: integer
        @param no: Article Number
        @type  article_dic : dictionary
        @param article_dic : Article Dictionary
        @type board_name: string
        @param board_name : BBS Name
        @rtype: boolean, string
        @return:
            1. Modify 성공: True, Article Number
            2. Modify 실패:
		1. 존재하지 않는 게시물번호: False, "ARTICLE_NOT_EXIST"
		2. 존재하지 않는 게시판: False, "BOARD_NOT_EXIST"
		3. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		4. 수정 권한이 없음: False, "NO_PERMISSION"
		5. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
	try:
	    self.articles[board_name][article_no] = article_dic
	except KeyError:
	    return False, "BOARD_NOT_EXIST"
	    return False, "ARTICLE_NOT_EXIST"


    def delete(self, session_key, board_name, no):
        """
        DB에 해당하는 글 삭제

        >>> article.delete(session_key, "garbages", 300)
	True, "OK"
        
        @type  session_key: string
        @param session_key: User Key
        @type  no: number
        @param no: Article Number
        @type board_name: string
        @param board_name : BBS Name
        @rtype: boolean, string 
        @return:
            1. Delete 성공: True, "OK"
	    2. Delete 실패:
		1. 존재하지 않는 게시물번호: False, "ARTICLE_NOT_EXIST"
		2. 존재하지 않는 게시판: False, "BOARD_NOT_EXIST"
		3. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		4. 수정 권한이 없음: False, "NO_PERMISSION"
		5. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
	try:
	    self.articles[board_name][article_no] = "삭제된 게시글 입니다."
	except KeyError:
	    return False, "BOARD_NOT_EXIST"
	    return False, "ARTICLE_NOT_EXIST"
	

	
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
        @rtype: boolean, list
        @return:
            1. 리스트 읽어오기 성공: True, Article List
	    2. 리스트 읽어오기 실패:
		1. 존재하지 않는 게시판: False, "BOARD_NOT_EXIST"
		2. 페이지 번호 오류: False, "WRONG_PAGENUM" 
		3. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
	article_list = []
	try:
	    for no in len(self.articles[board_name]):
		article_list.append(self.articles[board_name][no])
	    return article_list 
	except KeyError:
	    return False, "BOARD_NOT_EXIST"
	     

    def board_list(self, session_key):
        """
        게시판 목록 읽어오기

        >>> article.board_list(session_key)
	True, {"garbages": 84, "love": 0, "buynsell[com]": 4, ...]

        @type  session_key: string
        @param session_key: User Key
        @rtype: boolean, list
        @return:
            1. 리스트 읽어오기 성공: True, Dictionary of boards with new article num
            2. 리스트 읽어오기 실패: False 
		1. 데이터베이스 오류: False, "DATABASE_ERROR"
        """
	board = []
	try:
	    for no in len(self.article):
		board.append(article[no])	
	    return True, board
	except:
	    return False, "NOT_IMPLEMENTED"
		


    def search(self, session_key, board_name, query_text, search_type, page=1, page_length=20):
        """
        게시물 검색

        >>> article.search(session_key, "garbages", "심영준바보", "All", 2, 18)
	True, [44, {"no": 1, "read_status": "N", "title": ...}, {"no": 2, "read_status": "R", "title": ...}, ...]

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
        @rtype: boolean, list
        @return:
            1. 검색 성공: True, Article List(리스트의 맨 첫 항목은 검색 결과수)
	    2. 검색 실패:
		1. 검색 결과가 존재하지 않음: False, "NOT_FOUND"
		2. 존재하지 않는 게시판: False, "BOARD_NOT_EXIST"
		3. 잘못된 페이지 번호: False, "WROND_PAGENUM"
		4. 로그인되지 않은 유저: False, "NOT_LOGGEDIN"
		5. 데이터베이스 오류: False, "DATABASE_ERROR"

        """
	return False, "NOT_IMPLEMENTED"
