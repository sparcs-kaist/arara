# -*- coding: utf-8 -*-

class ArticleManager(object):

    def __init__(self):
        pass

    def read(session_key, no, bbs_name):
        """
        DB로부터 게시글 하나를 읽어옴

        >>> article.read(session_key, 300, "garbages")

        @type  session_key: string
        @param session_key: User Key
        @type  no: number
        @param no: Article Number
        @type bbs_name: string
        @param bbs_name : BBS Name
        @rtype: dictionary
        @return:
            1. Read 성공: Article Dictionary
            2. Read 실패: False
        """

    def write (session_key, article_dic, bbs_name):
        """
        DB에 게시글 하나를 작성함

        >>> article.write(session_key, article_dic)

        @type  session_key: string
        @param session_key: User Key
        @type  article_dic: dictionary
        @param article_dic: Article Dictionary
        @type bbs_name: string
        @param bbs_name : BBS Name
        @rtype: integer
        @return:
            1. Write 성공: Article Number
            2. Write 실패: False
        """

    def modify(session_key, no, article_dic, bbs_name):
        """
        DB의 해당하는 게시글 수정

        >>> article.modify(session_key, 300, article_dic)

        @type  session_key: string
        @param session_key: User Key
        @type  no: integer
        @param no: Article Number
        @type  article_dic : dictionary
        @param article_dic : Article Dictionary
        @type bbs_name: string
        @param bbs_name : BBS Name
        @rtype: integer
        @return:
            1. Modify 성공: Article Number
            2. Modify 실패: False
        """

    def delete(session_key, no, bbs_name):
        """
        DB에 해당하는 글 삭제

        >>> article.delete(session_key, 300)
        
        @type  session_key: string
        @param session_key: User Key
        @type  no: number
        @param no: Article Number
        @type bbs_name: string
        @param bbs_name : BBS Name
        @rtype: boolean
        @return:
            1. Delete 성공: True
            2. Delete 실패: False
        """

    def listshow(session_key, bbs_name, page=1, page_length=20):
        """
        게시판의 리스트 읽어오기

        >>> article.listshow(session_key, "garbages")

        @type  session_key: string
        @param session_key: User Key
        @type bbs_name: string
        @param bbs_name : BBS Name
        @type  page: integer
        @param page: Page Number to Request
        @type  page_length: integer
        @param page_length: Count of Article on a Page
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: Article List
            2. 리스트 읽어오기 실패: False
        """

    def search(session_key, bbs_name, query_text, search_type, page=1, page_length=20):
        """
        게시물 검색

        >>> article.search(session_key, "garbages", "심영준바보", "All")

        @type  session_key: string
        @param session_key: User Key
        @type  bbs_name: string
        @param bbs_name: BBS Name
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

