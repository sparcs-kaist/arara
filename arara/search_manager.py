# -*- coding: utf-8 -*-
import xmlrpclib
import time
import logging

from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import and_, or_, not_

from arara.util import require_login, filter_dict
from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara.util import datetime2timestamp
from arara.util import smart_unicode
from arara_thrift.ttypes import *
from arara import arara_manager
from arara import model
from etc.arara_settings import *

log_method_call = log_method_call_with_source('search_manager')
log_method_call_important = log_method_call_with_source_important('search_manager')

READ_ARTICLE_WHITELIST = ('id', 'title', 'contsent', 'last_modified_date', 'deleted', 'blacklisted', 'author_username', 'vote', 'date', 'hit', 'depth', 'root_id', 'is_searchable')
SEARCH_ARTICLE_WHITELIST = ('id', 'title', 'heading', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'author_nickname', 'author_id', 'positive_vote', 'negative_vote', 'hit', 'content', 'board_name')
SEARCH_DICT = ('title', 'content', 'author_nickname', 'author_username', 'date', 'query')

class SearchManager(arara_manager.ARAraManager):
    '''
    게시물 검색 기능을 담당하는 클래스
    '''


    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
        if item_dict.has_key('author_id'):
            item_dict['author_username'] = item.author.username
            item_dict['author_nickname'] = item.author.nickname
            del item_dict['author_id']
        if item_dict.has_key('board_id'):
            item_dict['board_name'] = item.board.board_name
            del item_dict['board_id']
        if item_dict.has_key('heading_id'):
            if item.heading == None:
                item_dict['heading'] = u''
            else:
                item_dict['heading'] = item.heading.heading
        if item_dict.has_key('root_id'):
            if not item_dict['root_id']:
                item_dict['root_id'] = item_dict['id']
	if item_dict.has_key('date'):
	    item_dict['date'] = datetime2timestamp(item_dict['date'])
	if item_dict.has_key('last_modified_date'):
	    item_dict['last_modified_date'] = datetime2timestamp(item_dict['last_modified_date'])
        if whitelist:
            filtered_dict = filter_dict(item_dict, whitelist)
        else:
            filtered_dict = item_dict
        return filtered_dict

    def _get_dict_list(self, raw_list, whitelist=None):
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist)
            return_list.append(Article(**filtered_dict))
        return return_list

    def _get_board(self, session, board_name):
        try:
            board = session.query(model.Board).filter_by(board_name=smart_unicode(board_name)).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation("board does not exist")
        return board

    def register_article(self):
        '''
        K-Search 에 게시물을 등록하는 함수였으나,
        현재 K-Search 가 작동하지 않아 Deprecated.
        '''
        raise InternalError("Deprecated")

    @require_login
    @log_method_call
    def ksearch(self, session_key, query_text, page=1, page_length=20):
        '''
        K-Search 를 사용하여 검색을 하는 함수였으나,
        현재 K-Search 가 작동하지 않아 Deprecated.
        '''
        raise InternalError('Deprecated')

    def _get_heading_id(self, session, board, heading):
        '''
        Internal Function - 주어진 heading 객체를 찾아낸다. (ArticleManager._get_heading 을 그대로 참고하여 만들어짐)

        @type  session: SQLAlchemy Session object
        @param session: 현재 사용중인 session
        @type  board: Board object
        @param board: 선택된 게시판 object
        @type  heading: unicode string
        @param heading: 선택한 말머리
        @rtype : BoardHeading object
        @return:
            1. 선택된 BoardHeading 객체 (단, heading == u"" 일 때는 None)
            2. 실패:
                TODO 구현할 것
        '''
        try:
            if heading == u"":
                return None
            return session.query(model.BoardHeading).filter_by(board=board, heading=heading).one().id
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('heading not exist')


    def _filter_query_dict(self, all_flag, query_dict):
        '''
        게시물 검색을 위해 all_flag 와 query_dict 파라메터를 바탕으로
        올바른 query_dict 를 만들어낸다.

        @type  all_flag: bool
        @param all_flag: <주석 필요>
        @type  query_dict: ttypes.SearchQuery
        @param query_dict: <주석 필요>
        @rtype: dict
        @return: <주석 필요>
        '''
        query_dict = query_dict.__dict__
        if len(query_dict) < 1:
            raise InvalidOperation('wrong dictionary')

        if all_flag:
            if not query_dict.has_key('query') or not query_dict['query']:
                raise InvalidOperation('wrong dictionary')
            return {'query': query_dict['query']}
        else:
            result = {}
            for key in query_dict.keys():
                if not query_dict[key]:
                    del query_dict[key]
                elif not key in SEARCH_DICT:
                    raise InvalidOperation('wrong dictionary')
                else:
                    result[key] = query_dict[key]
            return result

    def _get_basic_search_query(self, session, board_name, heading_name, include_all_headings):
        '''
        Search 에서 사용될 Basic Query 를 돌려준다.

        @type  session: model.Session
        @param session: SQLAlchemy Session
        @type  board_name: string
        @param board_name: 검색할 게시판
        @type  heading_name: string
        @param heading_name: 검색할 말머리
        @type  include_all_headings: bool
        @param include_all_headings: 모든 말머리를 포함할 것인가?
        '''
        # TODO: ArticleManager 에도 get_basic_query 가 있는데 그걸 응용하면 어떨까
        # TODO: Board 객체가 필요한가?
        query = session.query(model.Article).filter_by(is_searchable=True).filter_by(destroyed=False) # TODO: Test is needed
        if board_name != u'':
            board = self._get_board(session, board_name)
            query = query.filter_by(board_id=board.id)
            # 말머리 한정은 board 가 정해져 있어야만 가능하다
            if not include_all_headings:
                heading_id = self._get_heading_id(session, board, heading_name)
                query = query.filter_by(heading_id= heading_id)

        return query

    def _get_like_attached_query(self, query, all_flag, query_dict):
        '''
        주어진 Query 에 검색 관련 쿼리를 추가한다. Like statement 등을 의미한다.

        @type  query: SQLAlchemy Query
        @param query: SQLAlchemy Query
        @type  all_flag: bool
        @param all_flag: 모든 조건을 포함할 것인지의 여부
        @type  query_dict: dict
        @param query_dict: 검색 조건들

        '''
        if all_flag:
            query_text = query_dict['query']
            query_text = self._get_query_text(query_dict, 'query')
            query = query.join('author').filter(or_(
                    model.articles_table.c.title.like(query_text),
                    model.articles_table.c.content.like(query_text),
                    model.User.username.like(query_text),
                    model.User.nickname.like(query_text)))
        else:
            condition = None
            refer_dict = {'title': model.articles_table.c.title.like,
                    'content': model.articles_table.c.content.like,
                    'author_nickname': model.User.nickname.like,
                    'author_username': model.User.username.like,
                    'date': model.articles_table.c.date}
            for key in query_dict.keys():
                if key.upper() == "DATE":
                    continue #TODO: DATE SEARCH DISABLED!

                query_text = self._get_query_text(query_dict, key)
                if condition is None:
                    condition = refer_dict[key](query_text)
                else:
                    condition = or_(condition, refer_dict[key](query_text))

            query = query.join('author').filter(condition)

        return query

    def _extract_root_article_numbers(self, result):
        '''
        글의 목록으로부터 중복 없이 Root 글 번호의 목록을 뽑아낸다.

        @type  result: list<model.Article>
        @param result: 글의 목록
        @rtype: set
        @return: Root 글 번호 목록
        '''
        root_num = set()
        for one_article in result[::-1]:
            target_id = one_article.id
            if one_article.root:
                target_id = one_article.root.id
            if not target_id in root_num: # If root_num not exist
                root_num.add(target_id)
        return root_num

    def _get_page_offset(self, session, article_count, page, page_length):
        '''
        @type  session: model.Session
        @param session: SQLAlchemy Session
        @type  article_count: int
        @param article_count: 전체 글의 수
        @type  page: int
        @param page: 쪽번호
        @type  page_length: int
        @param page_length: 쪽마다 있는 글의 수
        @rtype: int, int, int
        @return:
            offset, last, last_page
        '''

        offset = page_length * (page - 1)
        last = offset + page_length
        last_page = int(article_count / page_length)
        if article_count % page_length != 0:
            last_page += 1
        elif article_count == 0:
            last_page += 1
        if page > last_page:
            session.close()
            raise InvalidOperation('wrong pagenum')

        return offset, last, last_page

    def _get_condition(self, root_num):
        '''
        root_num 에 주어진 글만 가져오는 condition 을 만든다.

        @type  root_num: list<int>
        @param root_num: 가져올 글의 목록
        @rtype: SQLAlchemy Condition
        @return: 그 글만 가져오는 condition
        '''
        condition = None
        if root_num: # If there is any element in the root_num set make condition
            condition = (model.Article.id == root_num[0])
            for one_id in root_num[1:]:
                current_condition = (model.Article.id == one_id)
                condition = or_(condition, current_condition)
        else: 
            # If there is no element in the root_num set, make condition that doesn't exist
            # Without this process, the condition would have None value so filter will be ignored
            # That was the reason of showing all the articles if there is no articles matches with query.
            condition = (model.Article.id == -1)

        return condition

    @require_login
    @log_method_call_important
    def search(self, session_key, all_flag, board_name, heading_name, query_dict, page=1, page_length=20, include_all_headings = True):
        '''
        게시물 검색

        전체검색이 아닐경우 query_dic에
        'title', 'content', 'author_nickname', 'author_username', 'date'중
        최소 한가지 이상의 조건을 넣어 보내면 주어진 조건에 대하여 AND 검색된다.
        
        (2008/11/05 02:04:pipoket)
        현재 OR검색이 수행되도록 변경하였음. 테스트 수정중

        전체검색을 하고 싶으면 all_flag를 true로 하면 된다.
        
        전체 검색의 경우 search_dic에 'query' 조건을 넣어 보내준다.
        전체 검색일 때 search_dic에 'content'이외의 키가 있을 경우
        WRONG_DICTIONARY 에러를 리턴한다.

        검색을 요청할 때 board_name을 지정하면, 그 보드만 검색을,
        board_name을 u''(string)로 지정하면 전체 보드 검색을 시도한다.

        기본적으로 전체검색은 K-Search를 사용하지만,
        K-Search가 비정상적으로 작동할경우 자체 쿼리 검색을 사용한다.
        (2010/12/06 combacsa: K-Search 관련 검색 코드를 제거.

        all_flag 'TRUE'  ==> query_dict {'query': 'QUERY TEXT'}
        all_flag 'FALSE' ==> query_dict {'title': '...', 'content': '...',
        'author_nickname': '...', 'author_username': '...', 'date': '...'}

        date 조건의 경우 YYYYMMDDHHmmSS (ex 20080301123423) 식으로 보내준다.
        
        @2008년 4월 3일부터 2008년 4월 5일까지의 게시물 20080403~20080405
        @2008년 4월 3일 이후의 게시물 20080403~
        @2008년 4월 3일 까지의 게시물 ~20080403

        **date는 현재 구현되지 않았음. 값을 넘겨도 무시됨 (2008.08.25 00:09)

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  all_flag: bool
        @param all_flag: Search all or not
        @type  board_name: string
        @param board_name: BBS Name
        @type  heading_name: string
        @param heading_name: 검색하고자 하는 말머리 한정 (board_name 주어졌을 때)
        @type  query_dict: ttypes.SearchQuery
        @param query_dict: Search Dictionary
        @type  page: int
        @param page: Page Number to Request
        @type  page_length: int
        @param page_length: Count of Article on a page
        @type  include_all_headings: bool
        @param include_all_headings: 모든 말머리를 대상으로 하는 검색인지 여부 (board_name 주어졌을 때)
        @rtype: ttypes.ArticleSearchResult
        @return:
            1. 검색성공: Search Result Dictionary ('hit': '검색결과', 'results': '결과 수', 'search_time': '검색 소요 시간', 'last_page': '마지막 페이지 번호')
            2. 검색 실패:
                1. 잘못된 query_dic: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 잘못된 페이지번호: InvalidOperation Exception
                4. 잘못된 날짜 형식: InvalidOperation Exception
                5. 로그인되지 않은 유저: NotLoggedIn Exception
                6. 데이터베이스 오류: InternalError Exception
        '''
        # QueryDict 를 정돈한다.
        query_dict = self._filter_query_dict(all_flag, query_dict)

        session = model.Session()
        ret_dict = {}

        start_time = time.time()

        # Board Name, Heading Name 등의 정보로부터 기본 query 를 얻는다
        query = self._get_basic_search_query(session, board_name, heading_name, include_all_headings)

        # 검색 기능 (스트링 검색) 이 포함된 Query 로 발전시킨다
        query = self._get_like_attached_query(query, all_flag, query_dict)

        # 마무리로 쿼리에 글 번호 순서로의 정렬을 덧씌우고 Fetch.
        # TODO: 어차피 뒤에서 root_num 으로 sort 하는데 여기 글번호 순서 정렬이 필요한가?
        result = query.order_by(model.Article.id.desc()).all()

        # 검색 결과에는 많은 글이 있을 것이나, Root 글 외에는 표시되어서는 안 된다.
        # 따라서 글 목록에 Root 만 표시되도록 하려면, 검색 결과로부터 Root 정보만
        # 뽑아내어 중복 없게 하여야 한다.
        root_num = self._extract_root_article_numbers(result)

        # Page 번호 계산하기
        article_count = len(root_num)
        # TODO: 이 부분은 Article Manager 와 거의 완전히 겹치는 듯 싶다.
        offset, last, last_page = self._get_page_offset(session, article_count, page, page_length)

        # (pipoket): Solution for maximum recursion depth exceeded exception
        # Filter out the unnecessary article numbers from the root_num set
        root_num = list(root_num)
        root_num.sort()
        root_num.reverse()
        root_num = root_num[offset:last]

        # Now we have all the root id we need. Query them!
        condition = self._get_condition(root_num)

        # Okay, I think everthing is prepared. Let's query the final result!
        # article_count, offset, last are moved up to the root_num set filtering part above
        query = session.query(model.Article).filter(condition)
        result = query.order_by(model.Article.id.desc()).all()

        end_time = time.time()

        search_list = list(result)

        session.close()

        # ArticleManager.get_article_list() 의 하단부 참고
        last_reply_ids = [article.last_reply_id for article in search_list]
        search_list    = [Article(**self._get_dict(article, SEARCH_ARTICLE_WHITELIST)) for article in search_list]
        search_list    = ArticleSearchResult(hit=search_list,
                last_page=last_page,
                results=article_count,
                search_time=end_time - start_time)

        # ArticleManager.article_list() 의 하단부 참고
        user_id = self.engine.login_manager.get_user_id_wo_error(session_key)
        self.engine.article_manager.put_user_specific_info(user_id, search_list, last_reply_ids)

        return search_list

    def _get_query_text(self, query_dict, key):
        query_text = unicode('%' + query_dict[key] + '%')
        return query_text

    __public__ = [
            register_article,
            ksearch,
            search]
