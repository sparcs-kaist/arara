# -*- coding: utf-8 -*-
import xmlrpclib
import time

from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import and_, or_, not_

from arara.util import require_login, filter_dict
from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara import model

READ_ARTICLE_WHITELIST = ('id', 'title', 'contsent', 'last_modified_date', 'deleted', 'blacklisted', 'author_username', 'vote', 'date', 'hit', 'depth', 'root_id', 'is_searchable')
SEARCH_ARTICLE_WHITELIST = ('id', 'title', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'author_nickname', 'vote', 'hit', 'content')
SEARCH_DICT = ('title', 'content', 'author_nickname', 'author_username', 'date')
api_server_address = 'http://nan.sparcs.org:9000/api'
api_key = '54ebf56de7684dba0d69bffc9702e1b4'

class SearchManager(object):
    '''
    게시물 검색 기능을 담당하는 클래스
    '''

    def __init__(self):
        pass

    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
        if item_dict.has_key('author_id'):
            item_dict['author_username'] = item.author.username
            item_dict['author_nickname'] = item.author.nickname
            del item_dict['author_id']
        if item_dict.has_key('board_id'):
            item_dict['board_name'] = item.board.board_name
            del item_dict['board_id']
        if item_dict.has_key('root_id'):
            if not item_dict['root_id']:
                item_dict['root_id'] = item_dict['id']
        if item_dict.has_key('content'):
            if whitelist == SEARCH_ARTICLE_WHITELIST:
                item_dict['content'] = item_dict['content'][:40]
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

    def ksearch(self, query_text, page=1, page_length=20):
        '''
        K-Search를 이용한 게시물 검색

        @type  query_text: string
        @param query_text: Text to Query
        @type  page: integer
        @param page: Page Number
        @type  page_length: integer
        @param page_length: Count of Articles on a page
        '''
        search_manager = xmlrpclib.Server('http://nan.sparcs.org:9000/api')
        query = str(query_text) + ' source:arara'
        result = search_manager.search('00000000000000000000000000000000', query)
        for one_result in result['hits']:
            if one_result.has_key('uri'):
                parsed_uri = one_result['uri'].rsplit('/', 2)
                one_result['id'] = parsed_uri[::-1][0]
                one_result['board_name'] = parsed_uri[::-1][1]
        return True, result

    def _search_via_ksearch(self, query_text, page=1, page_length=20):
        # XXX: Still Working...
        return False, 'KSEARCH_DEAD'
        #try:
        #    ret, result = ksearch(query_text, page, page_length)
        #except:
        #    return False, 'KSEARCH_DEAD'
        #if not ret:
        #    return False, 'KSEARCH_DEAD'
        #return ret, result

    def search(self, session_key, all_flag, board_name, query_dict, page=1, page_length=20):
        '''
        게시물 검색

        전체검색이 아닐경우 query_dic에
        'title', 'content', 'author_nickname', 'author_username', 'date'중
        최소 한가지 이상의 조건을 넣어 보내면 주어진 조건에 대하여 AND 검색된다.

        전체검색을 하고 싶으면 all_flag를 true로 하면 된다.
        
        전체 검색의 경우 search_dic에 'query' 조건을 넣어 보내준다.
        전체 검색일 때 search_dic에 'content'이외의 키가 있을 경우
        WRONG_DICTIONARY 에러를 리턴한다.

        검색을 요청할 때 board_name을 지정하면, 그 보드만 검색을,
        board_name을 'no_board'(string)로 지정하면 전체 보드 검색을 시도한다.

        기본적으로 전체검색은 K-Search를 사용하지만,
        K-Search가 비정상적으로 작동할경우 자체 쿼리 검색을 사용한다.

        all_flag 'TRUE'  ==> query_dict {'query': 'QUERY TEXT'}
        all_flag 'FALSE' ==> query_dict {'title': '...', 'content': '...',
        'author_nickname': '...', 'author_username': '...', 'date': '...'}

        date 조건의 경우 YYYYMMDDHHmmSS (ex 20080301123423) 식으로 보내준다.
        
        @2008년 4월 3일부터 2008년 4월 5일까지의 게시물 20080403~20080405
        @2008년 4월 3일 이후의 게시물 20080403~
        @2008년 4월 3일 까지의 게시물 ~20080403

        **date는 현재 구현되지 않았음. 값을 넘겨도 무시됨 (2008.08.25 00:09)

        @type  session_key: string
        @param session_key: User Key
        @type  all_flag: boolean
        @param all_flag: Search all or not
        @type  board_name: string
        @param board_name: BBS Name
        @type  query_dict: dictionary
        @param query_dict: Search Dictionary
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
        if not len(query_dict) > 0:
            return False, 'WRONG_DICTIONARY'

        for key in query_dict.keys():
            if all_flag:
                if not key == 'query':
                    return False, 'WRONG_DICTIONARY'
            else:
                if not key in SEARCH_DICT:
                    return False, 'WRONG_DICTIONARY'

        session = model.Session()
        ret_dict = {}

        start_time = time.time()

        if board_name.upper() == 'NO_BOARD':
            board = None
        else:
            try:
                board = session.query(model.Board).filter_by(board_name=board_name).one()
            except InvalidRequestError:
                session.close()
                return False, 'BOARD_NOT_EXIST'
                
        query = session.query(model.Article).filter_by(is_searchable=True)

        if board:
            query = query.filter_by(board_id=board.id)

        if all_flag:
            query_text = query_dict['query']
            ret, result = self._search_via_ksearch(query, page, page_length)
            if ret:
                return ret, result
            else:
                # I think K-Search is dead, so let's search it by query.
                query_text = self._get_query_text(query_dict, 'query')
                query = query.join('author').filter(or_(
                        model.articles_table.c.title.like(query_text),
                        model.articles_table.c.content.like(query_text),
                        model.User.username.like(query_text),
                        model.User.nickname.like(query_text)))
        else:
            if query_dict.has_key('title'):
                query_text = self._get_query_text(query_dict, 'title')
                query = query.filter(
                        model.articles_table.c.title.like(query_text))
            if query_dict.has_key('content'):
                query_text = self._get_query_text(query_dict, 'content')
                query = query.filter(
                        model.articles_table.c.content.like(query_text))
            if query_dict.has_key('author_nickname'):
                query_text = self._get_query_text(query_dict, 'author_nickname')
                try:
                    user_list = session.query(model.User).filter(
                            model.users_table.c.nickname.like(query_text)).all()
                except Exception:
                    session.close()
                    raise
                if len(user_list) > 0:
                    for one_user in user_list:
                        query = query.filter(or_(
                            model.articles_table.c.author_id==one_user.id))
                else:
                    query = query.filter_by(author_id=-1)
            if query_dict.has_key('author_username'):
                query_text = self._get_query_text(query_dict, 'author_username')
                try:
                    user_list = session.query(model.User).filter(
                            model.users_table.c.username.like(query_text)).all()
                except Exception:
                    session.close()
                    raise
                if len(user_list) > 0:
                    for one_user in user_list:
                        query = query.filter(or_(
                            model.articles_table.c.author_id==one_user.id))
                else:
                    query = query.filter_by(author_id=-1)
            if query_dict.has_key('date'):
                pass

        article_count = query.count()
        last_page = int(article_count / page_length)
        if article_count % page_length != 0:
            last_page += 1
        elif article_count == 0:
            last_page += 1
        if page > last_page:
            session.close()
            return False, 'WRONG_PAGENUM'
        offset = page_length * (page - 1)
        last = offset + page_length
        result = query[offset:last].order_by(model.Article.id.desc()).all()
        end_time = time.time()

        search_dict_list = self._get_dict_list(result, SEARCH_ARTICLE_WHITELIST)
        ret_dict['hit'] = search_dict_list
        ret_dict['results'] = article_count
        ret_dict['search_time'] = str(end_time-start_time)
        ret_dict['last_page'] = last_page
        session.close()
        return True, ret_dict

    def _get_query_text(self, query_dict, key):
        query_text = unicode('%' + query_dict[key] + '%')
        return query_text

if __name__ == "__main__":
    pass
