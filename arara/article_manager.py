# -*- coding: utf-8 -*-

class ArticleManager(object):
    """
    게시글 및 검색 처리 클래스
    """

    def __init__(self):
        pass

    def read(session_key, no, board_name):
        """
        DB로부터 게시글 하나를 읽어옴

        >>> article.read(session_key, 300, "garbages")

	    - Current Article Dictionary { no, read_status, title, author, date, hit, vote }

        @type  session_key: string
        @param session_key: User Key
        @type  no: number
        @param no: Article Number
        @type board_name: string
        @param board_name : BBS Name
        @rtype: dictionary
        @return:
            1. Read 성공: Article Dictionary
            2. Read 실패: False
        """

    def write (session_key, article_dic, board_name):
        """
        DB에 게시글 하나를 작성함

        >>> article.write(session_key, article_dic, "garbages")

        @type  session_key: string
        @param session_key: User Key
        @type  article_dic: dictionary
        @param article_dic: Article Dictionary
        @type board_name: string
        @param board_name : BBS Name
        @rtype: integer
        @return:
            1. Write 성공: Article Number
            2. Write 실패: False
        """

    def modify(session_key, no, article_dic, board_name):
        """
        DB의 해당하는 게시글 수정

        >>> article.modify(session_key, 300, article_dic, "garbages")

        @type  session_key: string
        @param session_key: User Key
        @type  no: integer
        @param no: Article Number
        @type  article_dic : dictionary
        @param article_dic : Article Dictionary
        @type board_name: string
        @param board_name : BBS Name
        @rtype: integer
        @return:
            1. Modify 성공: Article Number
            2. Modify 실패: False
        """

    def delete(session_key, no, board_name):
        """
        DB에 해당하는 글 삭제

        >>> article.delete(session_key, 300, "garbages")
        
        @type  session_key: string
        @param session_key: User Key
        @type  no: number
        @param no: Article Number
        @type board_name: string
        @param board_name : BBS Name
        @rtype: boolean
        @return:
            1. Delete 성공: True
            2. Delete 실패: False
        """

    def articlelist(session_key, board_name, page=1, page_length=20):
        """
        게시판의 게시글 목록 읽어오기

        >>> article.articlelist(session_key, "garbages", 2, 18)

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
            1. 리스트 읽어오기 성공: Article List
            2. 리스트 읽어오기 실패: False
        """

    def boardlist(session_key, board_name, page=1, page_length=20):
        """
        게시판 목록 읽어오기

        >>> article.boardlist(session_key, "garbages", 2, 18)

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
            1. 리스트 읽어오기 성공: Article List
            2. 리스트 읽어오기 실패: False
        """

    def search(session_key, board_name, query_text, search_type, page=1, page_length=20):
        """
        게시물 검색

        >>> article.search(session_key, "garbages", "심영준바보", "All", 2, 18)

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
            1. 검색 성공: Article List
            2. 검색 실패: False
        """

