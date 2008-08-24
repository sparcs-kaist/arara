# -*- coding: utf-8 -*-
import xmlrpclib

from arara.util import require_login, filter_dict
from arara import model

READ_ARTICLE_WHITELIST = ('id', 'title', 'content', 'last_modified_date', 'deleted', 'blacklisted', 'author_username', 'vote', 'date', 'hit', 'depth', 'root_id', 'is_searchable')
SEARCH_DICT = ('title', 'content', 'author_nick', 'author_username', 'date')
api_server_address = 'http://nan.sparcs.org:9000/api'
api_key = '54ebf56de7684dba0d69bffc9702e1b4'

class SearchManager(object):
    '''
    K-Search에 현재 게시물들을 추가하는 클래스
    '''

    def __init__(self):
        pass

    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
        if item_dict.has_key('author_id'):
            item_dict['author_username'] = item.author.username
            del item_dict['author_id']
        if item_dict.has_key('board_id'):
            item_dict['board_name'] = item.board.board_name
            del item_dict['board_id']
        if item_dict.has_key('root_id'):
            if not item_dict['root_id']:
                item_dict['root_id'] = item_dict['id']
        if whitelist:
            filtered_dict = filter_dict(item_dict, whitelist)
        else:
            filtered_dict = item_dict
        return filtered_dict

    def _get_dict_list(self, raw_list, whitelist=None):
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist)
            return_list.append(filtered_dict)
        return return_list

    def _set_board_manager(self, board_manager):
        self.board_manager = board_manager

    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    def register_article(self):
        ret, sess = self.login_manager.login('SYSOP', 'SYSOP', '234.234.234.234')
        if not ret:
            return False, 'NO_PERMISSION'
        #XXX SYSOP LOGIN MUST BE IMPLEMENTED HERE 
        ret, board_list = self.board_manager.get_board_list()
        if not ret:
            return False, 'DATABASE_ERROR'

        for board_info in board_list:
            session = model.Session()
            board_name = board_info['board_name']
            board = session.query(model.Board).filter_by(board_name=board_name).one()
            article_count = session.query(model.Article).filter_by(board_id=board.id).count()
            for article_no in range(1, article_count):
                article = session.query(model.Article).filter_by(id=article_no).one()
                article_dict = self._get_dict(article, READ_ARTICLE_WHITELIST)
                if article_dict['is_searchable']:
                    ksearch = xmlrpclib.Server(api_server_address)
                    uri = 'http://ara.kaist.ac.kr/' + board_name + '/' + str(article_no)
                    result = ksearch.index(api_key, 'ara', uri, article_dict['title'], article_dict['content'], 1.0, board_name)
                    assert result == 'OK'
            session.close()

    def ksearch(self):
        pass

    def search(self, session_key, all_flag, board_name, query_dic, page=1, page_length=20):
        '''
        게시물 검색

        전체검색이 아닐경우 query_dic에
        'title', 'content', 'author_nick', 'author_username', 'date'중
        최소 한가지 이상의 조건을 넣어 보내면 주어진 조건에 대하여 AND 검색된다.

        전체검색을 하고 싶으면 all_flag를 true로 하면 된다.
        
        전체 검색의 경우 search_dic에 'query' 조건을 넣어 보내준다.
        전체 검색일 때 search_dic에 'content'이외의 키가 있을 경우
        WRONG_DICTIONARY 에러를 리턴한다.

        전체검색일 때 board_name을 지정하면, 그 보드만 전체검색을,
        board_name을 'no_board'(string)로 지정하면 전체 보드 검색을 시도한다.

        기본적으로 전체검색은 K-Search를 사용하지만,
        K-Search가 비정상적으로 작동할경우 자체 쿼리 검색을 사용한다.

        all_flag 'TRUE'  ==> search_dic {'query': 'QUERY TEXT'}
        all_flag 'FALSE' ==> search_dic {'title': '...', 'content': '...',
        'author_nick': '...', 'author_username': '...', 'date': '...'}

        date 조건의 경우 YYYYMMDDHHmmSS (ex 20080301123423) 식으로 보내준다.
        
        > 2008년 4월 3일부터 2008년 4월 5일까지의 게시물 20080403~20080405
        > 2008년 4월 3일 이후의 게시물 20080403~
        > 2008년 4월 3일 까지의 게시물 ~20080403

        **date는 현재 구현되지 않았음. 값을 넘겨도 무시됨 (2008.08.25 00:09)

        @type  session_key: string
        @param session_key: User Key
        @type  all_flag: boolean
        @param all_flag: Search all or not
        @type  board_name: string
        @param board_name: BBS Name
        @type  query_dic: dictionary
        @param query_dic: Search Dictionary
        @type  page: integer
        @param page: Page Number to Request
        @type  page_length: integer
        @param page_length: Count of Article on a page
        @rtype: boolean, dictionary
        @return:
            1. 검색성공: True, Search Result Dictionary ('hit': '검색결과', 'results': '결과 수', 'search_time': '검색 소요 시간', 'last_page': '마지막 페이지 번호')
            2. 검색 실패:
                1. 잘못된 query_dic: False, 'WRONG_DICTIONARY'
                2. 존재하지 않는 게시판: False, 'BOARD_NOT_EXIST'
                3. 잘못된 페이지번호: False, 'WRONG_PAGENUM'
                4. 잘못된 날짜 형식: False, 'WRONG_DATE'
                5. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                6. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        pass

if __name__ == "__main__":
    pass
