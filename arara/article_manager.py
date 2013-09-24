# -*- coding: utf-8 -*-
import datetime
import time
import thread

from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy import and_, or_, not_, func
from sqlalchemy.orm import eagerload
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql import func, select

from libs import datetime2timestamp, filter_dict, smart_unicode
from arara import arara_manager
from arara import model
from arara.model import BOARD_TYPE_ANONYMOUS
from arara.util import require_login
from arara.util import log_method_call_with_source, log_method_call_with_source_duration, log_method_call_with_source_important

from arara_thrift.ttypes import *

log_method_call = log_method_call_with_source('article_manager')
log_method_call_duration = log_method_call_with_source_duration('article_manager')
log_method_call_important = log_method_call_with_source_important('article_manager')

# TODO: WRITE_ARTICLE_DICT 는 사실 쓰이지 않는다... SPEC 표시 용도일까?
WRITE_ARTICLE_DICT = ('title', 'heading', 'content')
READ_ARTICLE_WHITELIST = ('id', 'heading', 'title', 'content', 'last_modified_date', 'deleted', 'blacklisted', 'author_username', 'author_nickname', 'author_id', 'positive_vote', 'negative_vote', 'date', 'hit', 'depth', 'root_id', 'is_searchable', 'attach', 'board_name', 'anonymous')
LIST_ARTICLE_WHITELIST = ('id', 'title', 'heading', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'author_nickname', 'author_id', 'positive_vote', 'negative_vote', 'hit', 'board_name', 'anonymous')
# TODO SEARCH_ARTICLE_WHITELIST 는 왜 여기에도 있는 걸까?
SEARCH_ARTICLE_WHITELIST = ('id', 'title', 'heading', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'author_nickname', 'author_id', 'vote', 'hit', 'content')
BEST_ARTICLE_WHITELIST = ('id', 'title', 'date', 'last_modified_date', 'reply_count',
                    'deleted', 'author_username', 'author_nickname', 'author_id', 'positive_vote', 'negative_vote', 'hit', 'last_page', 'board_name', 'root_id')
RECENT_ARTICLE_WHITELIST = BEST_ARTICLE_WHITELIST

LIST_ORDER_ROOT_ID         = 0
LIST_ORDER_LAST_REPLY_DATE = 1

class ArticleManager(arara_manager.ARAraManager):
    '''
    글 (게시물) 과 관련된 거의 모든 일을 수행한다.

        - 게시물 읽기 / 쓰기 / 수정 / 삭제 / 목록 / 추천
        - 특수 목적의 글 목록 (투데이 / 위클리 베스트 등)

    주요 용어

        - 루트 글 : 답글이 아닌 글 (목록에 반드시 나오는 글)
        - 답글 : 루트 글 혹은 다른 답글에 귀속되어 있는 글
    '''

    def _article_thread_to_list(self, article_thread, blacklisted_userid):
        '''
        @type  article_thread: model.Article (children eager loaded)
        @param article_thread: list화 할 루트 글 객체
        @type  blacklisted_userid: set<int>
        @param blacklisted_userid: 주어진 사용자의 blacklist 목록
        @rtype: list<dict(READ_ARTICLE_WHITELIST applied)>
        @return: article_thread 로 주어진 루트 글과 여기에 속한 모든 답글들을 일렬로 세운 list
        '''
        # TODO: destroy 된 글을 중간에 보이지 않게 하기
        stack = []
        ret = []
        stack.append((article_thread, 1))
        while stack:
            art, dep = stack.pop()
            for child in art.children[::-1]:
                stack.append((child, dep + 1))
            dic = self._get_dict(art, READ_ARTICLE_WHITELIST)
            dic['depth'] = dep

            if dic['author_id'] in blacklisted_userid:
                dic['blacklisted'] = True
            else:
                dic['blacklisted'] = False

            ret.append(Article(**dic))

        return ret

    @log_method_call_duration
    def _get_best_article(self, session_key, board_id, count, time_to_filter, best_type, criteria):
        '''
        @type  sessino_key: string
        @param session_key: 사용자 Login Session
        @type  board_id: int
        @param board_id: best article 을 가져오고자 하는 board
        @type  count: int
        @param count: 몇 개의 best article 을 가져올 것인가?
        @type  time_to_filter: int
        @param time_to_filter: 몇 초 이내의 글만을 대상으로 할 것인가?
        @type  best_type: string
        @param best_type: 글 목록을 돌려줄 때 저장할 목록의 속성 (today / weekly)
        @type  criteria: string
        @param criteria: best article을 정할 기준 (vote / hit)
        @rtype: list<ttypes.Article>
        @return: Best Article들
        '''
        #TODO: Query 의 코드 중복 제거하기 (성능 분석 포함)
        #TODO: Query 부분과 글목록화 부분 분리하기
        #XXX(hodduc): root 글이 아닌 글도 포함하려면, 다음 쿼리에서 model.Article.root_id==None 부분만 지우면 된다.

        session = model.Session()
        time_to_filter = datetime.datetime.fromtimestamp(time.time()-time_to_filter)
        if board_id:
            query = session.query(model.Article).filter(and_(
                    model.Article.board_id==board_id,
                    model.Article.root_id==None,
                    model.Article.last_modified_date > time_to_filter,
                    model.Article.board.has(model.Board.hide==False),
                    model.Article.board.has(model.Board.deleted==False),
                    not_(model.Article.deleted==True),
                    model.Article.is_searchable==True))
        else:
            query = session.query(model.Article).filter(and_(
                    model.Article.root_id==None,
                    model.Article.last_modified_date > time_to_filter,
                    model.Article.board.has(model.Board.hide==False),
                    model.Article.board.has(model.Board.deleted==False),
                    not_(model.Article.deleted==True),
                    model.Article.is_searchable==True))

        if criteria=="vote":
            best_article = query.order_by(model.Article.positive_vote.desc()).order_by(model.Article.reply_count.desc()).order_by(model.Article.id.desc())[:count]
        else:
            best_article = query.order_by(model.Article.hit.desc()).order_by(model.Article.reply_count.desc()).order_by(model.Article.id.desc())[:count]
        best_article_dict_list = self._get_dict_list(best_article, BEST_ARTICLE_WHITELIST)
        session.close()

        best_article_list = list()
        for article in best_article_dict_list:
            article['type'] = best_type
            best_article_list.append(Article(**article))
        return best_article_list

    def _get_dict(self, item, whitelist=None):
        '''
        @type  item: model.Article
        @param item: dictionary 로 바꿀 객체 (여기서는 글)
        @type  whitelist: list
        @param whitelist: dictionary 에 남아있을 필드의 목록
        @rtype: dict
        @return: item 에서 whitelist 에 있는 필드만 남기고 적절히 dictionary 로 변환한 결과물
        '''
        # TODO: 여기서 할 필요가 없는 query (file 관련) filemanager 로 옮기기
        item_dict = item.__dict__

        item_dict['date'] = datetime2timestamp(item_dict['date'])
        item_dict['last_modified_date'] = datetime2timestamp(item_dict['last_modified_date'])
        item_dict['anonymous'] = False

        if not item_dict.get('title'):
            item_dict['title'] = u'Untitled'
        if 'author_id' in item_dict:
            item_dict['author_username'] = item.author.username
        if 'board_id' in item_dict:
            item_dict['board_name'] = item.board.board_name
            del item_dict['board_id']
            if item.board.type == BOARD_TYPE_ANONYMOUS:
                item_dict['anonymous'] = True
        if 'heading_id' in item_dict:
            if item.heading == None:
                item_dict['heading'] = u''
            else:
                item_dict['heading'] = item.heading.heading
        if not item_dict.get('root_id'):
            item_dict['root_id'] = item_dict['id']
        if 'content' in item_dict:
            if whitelist == SEARCH_ARTICLE_WHITELIST:
                item_dict['content'] = item_dict['content'][:40]
            if whitelist == READ_ARTICLE_WHITELIST:
                attach_list = self.engine.file_manager._get_attached_file_list(item.id)
                if attach_list:
                    item_dict['attach'] = attach_list

        if whitelist:
            return filter_dict(item_dict, whitelist)
        else:
            return item_dict

    def _get_dict_list(self, raw_list, whitelist=None):
        '''
        @type  raw_list: iterable(list, generator)<model.Article>
        @param raw_list: _get_dict 에 통과시키고 싶은 대상물의 모임
        @type  whitelist: list<string>
        @param whitelist: _get_dict 에 넘겨줄 whitelist
        @rtype: generator<dict(whitelist filtered)>
        @return: _get_dict 를 통과시킨 raw_list 의 원소들을 하나씩 yield
        '''
        for item in raw_list:
            yield self._get_dict(item, whitelist)

    def _get_article(self, session, board_id, article_id):
        '''
        Internal Function.
        SQLAlchemy 세션을 이용하여 (게시판의) 글을 하나 읽어온다.

        @type  session: SQLAlchemy session
        @param session: SQLAlchemy session
        @type  board_id: int
        @param board_id: 읽고자 하는 글이 있는 게시판의 id (단, None 일 때는 모든 게시판이라 가정)
        @type  article_id: int
        @param article_id: 읽고자 하는 글의 id
        @rtype: model.Article
        @return: 선택한 Article 객체
        '''
        try:
            if board_id:
                article = session.query(model.Article).filter_by(board_id=board_id, id=article_id).one()
            else:
                article = session.query(model.Article).filter_by(id = article_id).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation("article does not exist")
        return article

    def get_page_info(self, article_count, page, page_length):
        '''
        요청한 페이지에 해당되는 글의 번호 대역을 알아낸다.

        @type  article_count: int
        @param article_count: Query 의 모든 글의 갯수
        @type  page: int
        @param page: 글의 번호 대역을 알고자 하는 page
        @type  page_length: int
        @param page_length: 페이지당 글의 갯수
        @rtype: (int, int, int)
        @return: last page 번호, 주어진 page 의 첫 글의 위치, 마지막 글의 위치
        '''
        # part 1. last page 구하기 
        last_page = int(article_count / page_length)
        if article_count % page_length != 0:
            last_page += 1
        elif article_count == 0:
            last_page += 1

        # part 2. 페이지가 비정상 범위라면? InvalidOperation.
        if (page > last_page) or (page < 0):
            raise ValueError('WRONG_PAGENUM')

        # part 3. Page 의 시작 글과 끝 글의 번째수를 구한다.
        offset = page_length * (page - 1)
        last = offset + page_length

        return last_page, offset, last

    @log_method_call
    def get_today_best_list(self, count=5):
        '''
        전체 보드에서 투베를 가져오는 함수

        @type  count: int
        @param count: Number of today's best articles to get
        @rtype: list<ttypes.Article>
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. 데이터베이스 오류: InternalError Exception 
        '''
        return self._get_best_article(None, None, count, 86400, 'today', 'vote')

    @log_method_call
    def get_today_best_list_specific(self, board_name, count=5):
        '''
        해당 보드에서 투베를 가져오는 함수

        @type  board_name: string
        @param board_name: Board Name
        @type  count: int
        @param count: Number of today's best articles to get
        @rtype: list<ttypes.Article>
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: 굳이 위 함수(get_today_best_list)와 이 함수가 따로 존재할 필요가 있을까?
        board_id = self.engine.board_manager.get_board_id(board_name)
        return self._get_best_article(None, board_id, count, 86400, 'today', 'vote')

    @log_method_call
    def get_weekly_best_list(self, count=5):
        '''
        전체 보드에서 윅베를 가져오는 함수

        @type  count: int
        @param count: Number of weekly best articles to get
        @rtype: list<ttypes.Article>
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        return self._get_best_article(None, None, count, 604800, 'weekly', 'vote')

    @log_method_call
    def get_weekly_best_list_specific(self, board_name, count=5):
        '''
        해당 보드에서 윅베를 가져오는 함수

        @type  board_name: string
        @param board_name: Board Name
        @type  count: int
        @param count: Number of weekly best articles to get
        @rtype: list<ttypes.Article>
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: InvalidOperation Exception 
                2. 데이터베이스 오류: InternalError Exception
        '''
        board_id = self.engine.board_manager.get_board_id(board_name)
        return self._get_best_article(None, board_id, count, 604800, 'weekly', 'vote')

    @log_method_call
    def get_today_most_list(self, count=5):
        '''
        전체 보드에서 하루동안 가장 많이 읽힌 글을 가져오는 함수

        @type  count: int
        @param count: Number of today's most read articles to get
        @rtype: list<ttypes.Article>
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. 데이터베이스 오류: InternalError Exception 
        '''
        return self._get_best_article(None, None, count, 86400, 'today', 'hit')

    @log_method_call
    def get_today_most_list_specific(self, board_name, count=5):
        '''
        해당 보드에서 하루동안 가장 많이 읽힌 글을 가져오는 함수

        @type  board_name: string
        @param board_name: Board Name
        @type  count: int
        @param count: Number of today's most read articles to get
        @rtype: list<ttypes.Article>
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: 굳이 위 함수(get_today_best_list)와 이 함수가 따로 존재할 필요가 있을까?
        board_id = self.engine.board_manager.get_board_id(board_name)
        return self._get_best_article(None, board_id, count, 86400, 'today', 'hit')

    @log_method_call
    def get_weekly_most_list(self, count=5):
        '''
        전체 보드에서 윅베를 가져오는 함수

        @type  count: int
        @param count: Number of weekly most read articles to get
        @rtype: list<ttypes.Article>
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        return self._get_best_article(None, None, count, 604800, 'weekly', 'hit')

    @log_method_call
    def get_weekly_most_list_specific(self, board_name, count=5):
        '''
        해당 보드에서 윅베를 가져오는 함수

        @type  board_name: string
        @param board_name: Board Name
        @type  count: int
        @param count: Number of weekly most read articles to get
        @rtype: list<ttypes.Article>
        @return:
            1. 투베를 가져오는데 성공: Article list of Today's Best
            2. 투베를 가져오는데 실패:
                1. Not Existing Board: InvalidOperation Exception 
                2. 데이터베이스 오류: InternalError Exception
        '''
        board_id = self.engine.board_manager.get_board_id(board_name)
        return self._get_best_article(None, board_id, count, 604800, 'weekly', 'hit')


    def _get_blacklist_userid(self, user_id):
        '''
        주어진 사용자의 blacklist 목록을 가져온다.

        @type  user_id: int
        @param user_id: 사용자 고유 id
        @rtype: set<int>
        @return: 해당 사용자가 blacklist 등록한 사용자들의 id (-1 이 들어오면 빈 셋)
        '''
        if user_id == -1:
            return set()
        else:
            return set(self.engine.blacklist_manager._get_article_blacklisted_userid_list(user_id))

    def _get_basic_query(self, session, board_name, heading_name, include_all_headings):
        '''
        Internal.
        주어진 게시판 이름에 알맞는 SQLAlchemy Query 를 돌려준다. 이때 root_id 가 None 인 글만 목록에 포함된다.

        @type  session: SQLAlchemy Session
        @param session: SQLAlchemy Session
        @type  board_name: string
        @param board_name: 보드의 이름
        @type  heading_name: string
        @param heading_name: 말머리의 이름 (include_all_headings == True 일 때는 무시됨)
        @type  include_all_headings: Boolean
        @param include_all_headings: 모든 말머리에 대해 적용할 것인가의 여부
        @rtype: SQLAlchemy Query
        @return: 선택된 board_name, heading_name, include_all_headings 가 적용된 Query
        '''
        # TODO: 좀더 조립식으로 만들기 위해서는 board_name, heading_name 대신 board_id, heading_id 를 받아야지 않을까
        query = session.query(model.Article)

        if board_name != u'':
            # 해당 board 에 있는 글만 선택한다.
            board_id = self.engine.board_manager.get_board_id(board_name)
            query = query.filter_by(board_id=board_id, root_id=None, destroyed=False)

            if not include_all_headings:
                # 특정 말머리만 선택한다
                heading = self.engine.board_manager._get_heading_by_boardid(session, board_id, heading_name)
                query = query.filter_by(heading=heading)
        else:
            # 모든 board 에 있는 글을 선택한다. 단 hide 된 보드나 delete 된 보드는 제외한다.
            query = query.filter(and_(
                    model.Article.root_id==None,
                    model.Article.destroyed==False,
                    model.Article.board.has(model.Board.hide==False),
                    model.Article.board.has(model.Board.deleted==False),
                    not_(model.Article.board.has(model.Board.type==2))))

        return query

    def _get_ordered_query(self, session, query, order_by):
        '''
        Internal.
        주어진 Query 에 적합한 order_by 결과를 돌려준다.

        @type  session: SQLAlchemy Session
        @param session: SQLAlchemy Session
        @type  query: SQLAlchemy Query
        @param query: SQLAlchemy Query
        @type  order_by: int
        @param order_by: 원하는 게시물 정렬 방식. 보통 LIST_ORDER_ROOT_ID.
        @rtype: SQLAlchemy Query
        @return: 정렬방식이 적용된 SQLAlchemy Query
        '''
        if order_by == LIST_ORDER_ROOT_ID:
            return query.order_by(model.Article.id.desc())
        elif order_by == LIST_ORDER_LAST_REPLY_DATE:
            return query.order_by(model.Article.last_reply_date.desc())
        else:
            session.close()
            raise InvalidOperation("WRONG_ORDERING")

    def get_article_list_by_username(self, username):
        '''
        해당 username이 작성한 글 번호 리스트를 반환한다.

        @type  username: str
        @param username: 글을 가져올 유저 아이디
        @return: username에 해당하는 user가 쓴 게시물의 목록
        '''
        session = model.Session()
        user_id = session.query(model.User).filter_by(username=username).first().id
        return session.query(model.Article).filter_by(author_id=user_id)

    def get_article_list(self, board_name, heading_name, page, page_length, include_all_headings=True, order_by=LIST_ORDER_ROOT_ID):
        '''
        게시물의 목록, 각 게시물에 마지막으로 달린 답글의 번호를 반환한다.

        @type  board_name: str
        @param board_name: 글을 가져올 게시판의 이름
        @type  heading_name: str
        @param heading_name: 가져올 글의 글머리 이름
        @type  page: int
        @param page: 글을 가져올 페이지의 번호
        @type  page_length: int
        @param page_length: 페이지당 글 갯수
        @type  include_all_headings: bool
        @param include_all_headings: 모든 글머리의 글을 가져올지에 대한 여부
        @type  order_by: int
        @param order_by: 정렬 방식 [LIST_ORDER_ROOT_ID, LIST_ORDER_LAST_REPLY_ID]
        @rtype: list<ttypes.ArticleList>, list<int>
        @return: 선택된 게시물의 목록, 각 게시물의 마지막 답글 번호의 목록
        '''
        session = model.Session()
        # 게시판, 선택된 말머리를 바탕으로 Query 생성
        desired_query = self._get_basic_query(session, board_name, heading_name, include_all_headings)
        article_count = desired_query.count()

        # 페이지 정보 확인, 불러올 게시물의 범위 확정
        try:
            last_page, offset, last = self.get_page_info(article_count, page, page_length)
        except ValueError as e:
            session.close()
            if str(e) == 'WRONG_PAGENUM':
                raise InvalidOperation(str(e))
            else:  # Unexpected Exception
                raise
 
        # 정렬 방식 적용, 범위에 있는 게시물 불러오기
        desired_query = self._get_ordered_query(session, desired_query, order_by)
        article_list  = desired_query[offset:last]

        session.close()

        # 게시물의 목록, 마지막 답글 번호 목록 정리
        last_reply_ids = [article.last_reply_id for article in article_list]
        article_list   = [Article(**self._get_dict(article, LIST_ARTICLE_WHITELIST)) for article in article_list]
        article_list   = ArticleList(hit=article_list, current_page=page, last_page=last_page, results=article_count)
 
        return article_list, last_reply_ids

    @log_method_call
    def put_user_specific_info(self, user_id, article_list, last_reply_id_list):
        '''
        게시물 목록에 각 사용자를 위한 다음의 정보들을 추가한다.

        (1) 새글/새 댓글 알림
        (2) Blacklist

        @type  user_id: int
        @param user_id: 사용자 고유 id (로그인하지 않은 사용자는 -1)
        @type  article_list: ttypes.ArticleList / ttypes.ArticleSearchResult
        @param article_list: 게시물 목록
        @type  last_reply_id_list: list<int>
        @param last_reply_id_list: 각 게시물의 마지막 글번호의 목록
        @rtype: void
        @return: 없음 (article_list 파라메터에 직접 수정을 가한다)
        '''
        if user_id == -1:
            # 로그인하지 않았으므로 모든 글은 새 글, 차단된 사용자는 없음
            for article in article_list.hit:
                article.read_status = 'N'
                article.blacklisted = False
                article.type = 'normal'
        else:
            root_id_list = [article.id for article in article_list.hit]
            # ReadStatusManager 와 BlacklistManager 로부터 정보 가져오기
            read_status_main = self.engine.read_status_manager.check_stats_by_id(user_id, root_id_list)
            read_status_sub  = self.engine.read_status_manager.check_stats_by_id(user_id, last_reply_id_list)
            blacklisted_users = self._get_blacklist_userid(user_id)
            for idx, article in enumerate(article_list.hit):
                # Root 글은 읽었는데 마지막 답글은 안 읽었다면 새 댓글
                # Root 글도 읽었고   마지막 답글도 읽었다면 다 읽은 글
                if read_status_main[idx] == 'R':
                    if read_status_sub[idx] == 'N':
                        article.read_status = 'U'
                    else:
                        article.read_status = 'R'
                else:
                    article.read_status = 'N'
                # Blacklist
                article.blacklisted = article.author_id in blacklisted_users
                # Article Type
                article.type = 'normal'

    @log_method_call
    def article_list(self, session_key, board_name, heading_name, page=1, page_length=20, include_all_headings=True):
        '''
        게시판의 게시글 목록 읽어오기

        @type  session_key: str
        @param session_key: 사용자 Login Session
        @type  board_name: str
        @param board_name: 게시판의 이름 / 모든 게시판은 "" 로 지정
        @type  heading_name: str
        @param heading_name: 가져올 글의 글머리 이름
        @type  page: int
        @param page: Page Number to Request
        @type  page_length: int
        @param page_length: Count of Article on a Page
        @type  include_all_headings: bool
        @param include_all_headings: 모든 글머리의 글을 가져올지에 대한 여부
        @rtype: ttypes.ArticleList
        @return:
            1. 리스트 읽어오기 성공: Article List
            2. 리스트 읽어오기 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 페이지 번호 오류: InvalidOperation Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        # page 번호가 0 이 들어오더라도 1로 교정
        if page == 0:
            page = 1

        # 사용자에 대한 정보 가져오기
        user_id = self.engine.login_manager.get_user_id_wo_error(session_key)
        listing_mode = self.engine.member_manager.get_listing_mode(user_id)

        # 게시물 목록 가져오기
        article_list, last_reply_ids = self.get_article_list(board_name, heading_name, page, page_length, include_all_headings, listing_mode)
        self.put_user_specific_info(user_id, article_list, last_reply_ids)

        return article_list

    @log_method_call_duration
    def _read_article(self, session, no):
        '''
        Internal Use Only.
        DB 로부터 "정말로" 게시글 하나를 읽어옴

        @type  session: model.Session
        @param session: SQLAlchemy Session
        @type  no: int
        @param no: 읽어올 글의 번호
        @rtype: model.Article
        @return:
            Eager Loading 이 적용된 Article 객체
        '''
        return session.query(model.Article).options(eagerload('children')).filter_by(id=no).one()

    @require_login
    @log_method_call_important
    def read_article(self, session_key, board_name, no):
        '''
        DB로부터 게시글 하나(Root 글일 경우 답글도 함께) 읽어옴

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  board_name: string
        @param board_name: 게시판 이름
        @type  no: int
        @param no: Article Number
        @rtype: list<ttypes.Article>
        @return:
            1. Read 성공: 선택한 글과 그 글에 딸린 글들의 list
            2. Read 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 데이터베이스 오류: InternalError Exception 
        '''

        session = model.Session()
        # TODO: 주어진 board_name 에 맞는지 check
        # TODO: require_login 거치는 횟수 줄이기
        user_id = self.engine.login_manager.get_user_id(session_key)
        blacklisted_userid = self._get_blacklist_userid(user_id)

        try:
            article = self._read_article(session, no)
            msg = self.engine.read_status_manager._check_stat(user_id, no)
            if msg == 'N':
                article.hit += 1
                session.commit()
        except InvalidRequestError:
            session.rollback()
            session.close()
            raise InvalidOperation('ARTICLE_NOT_EXIST')
        article_dict_list = self._article_thread_to_list(article, blacklisted_userid)
        self.engine.read_status_manager._mark_as_read_list(user_id, [x.id for x in article_dict_list])
        session.close()
        return article_dict_list

    def read_recent_article(self, session_key, board_name):
        '''
        DB로부터 주어진 게시판의 최근의 게시글 하나만을 읽어옴

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  board_name: string
        @param board_name: 게시판의 이름
        @rtype: list<ttypes.Article>
        @return:
            1. Read 성공: list<ttypes.Article>
            2. Read 실패:
                1. 최근 게시물이 존재하지 않음: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 데이터베이스 오류: InternalError Exception 
        '''
        # TODO: 위의 read_article 과 엮어서 조립식으로 만들기
        
        board_id = self.engine.board_manager.get_board_id(board_name)
        session = model.Session()
        user_id = self.engine.login_manager.get_user_id_wo_error(session_key)
        blacklisted_userid = self._get_blacklist_userid(user_id)

        try:
            article = session.query(model.Article).options(eagerload('children')).filter_by(board_id=board_id).order_by(model.Article.id.desc()).first()
            if article == None:
                raise InvalidOperation('ARTICLE_NOT_EXIST')
            msg = self.engine.read_status_manager.check_stat(session_key, article.id)
            if msg == 'N':
                article.hit += 1
                session.commit()
        except InvalidRequestError:
            session.rollback()
            session.close()
            raise InvalidOperation('ARTICLE_NOT_EXIST')

        article_dict_list = self._article_thread_to_list(article, blacklisted_userid)
        self.engine.read_status_manager._mark_as_read_list(user_id, [x.id for x in article_dict_list])
        session.close()
        return article_dict_list

    def _get_total_article_count(self, session, board_id, heading_id, include_all_headings = True):
        '''
        Internal.
        주어진 게시판에 있는 선택된 말머리에 해당되는 모든 글의 갯수를 센다.

        @type  session: SQLAlchemy Session
        @param session: 사용중인 session
        @type  board_id: int
        @param board_id: 글 갯수를 가져올 게시판의 id
        @type  heading_id: int
        @param heading_id: 글 갯수를 가져올 말머리의 id (없을 경우 None)
        @type  include_all_headings: bool
        @param include_all_headings: 모든 말머리를 가져올 것인지의 여부
        @rtype: int
        @return: 해당 게시판의 해당되는 말머리의 모든 글의 갯수
        '''
        query = session.query(model.Article)

        if board_id == None:
            query = query.filter(and_(
                    model.Article.root_id==None,
                    model.Article.destroyed==False,
                    model.Article.board.has(model.Board.hide==False),
                    model.Article.board.has(model.Board.deleted==False)))
        else:
            query = query.filter_by(board_id=board_id, root_id=None, destroyed=False)
            if not include_all_headings:
                query = query.filter_by(heading_id=heading_id)

        return query.count()

    @log_method_call_duration
    def _get_remaining_article_count(self, session, board_id, heading_id, no, include_all_headings = True, order_by = LIST_ORDER_ROOT_ID):
        '''
        Internal.
        주어진 게시판에 있는 선택된 말머리에 해당되는 글들 중 no 번 글 이후로 몇 개의 글이 있는지 센다.

        @type  session: SQLAlchemy Session
        @param session: 사용중인 session
        @type  board_id: int
        @param board_id: 글을 가져올 게시판의 id
        @type  heading_id: int
        @param heading_id: 목록에서 보여줄 선택된 말머리
        @type  no: int
        @param no: 글번호
        @type  include_all_headings: bool
        @param include_all_headings: 모든 말머리를 보여줄 것인지의 여부
        @type  order_by: int - LIST_ORDER
        @param order_by: 글 정렬 방식 (현재는 LIST_ORDER_ROOT_ID 만 테스트됨)
        @rtype: int
        @return: 해당 게시판의 해당되는 말머리에서 no 번 이후 게시된 글의 개수 
        '''
        query = session.query(model.Article)
        # query 조립 개시
        query = query.filter(model.Article.root_id==None)
        query = query.filter(model.Article.destroyed==False)
        if board_id == None:
            query = query.filter(model.Article.board.has(model.Board.hide==False))
            query = query.filter(model.Article.board.has(model.Board.deleted==False))
        else:
            query = query.filter(model.Article.board_id==board_id)
            if not include_all_headings:
                query = query.filter_by(heading_id=heading_id)
        # Listing 방식에 따른 정렬순서
        if order_by == LIST_ORDER_ROOT_ID:
            query = query.filter(model.Article.id > no)
        elif order_by == LIST_ORDER_LAST_REPLY_DATE:
            last_reply_date = self._get_article(session, board_id, no).last_reply_date
            query = query.filter(model.Article.last_reply_date > last_reply_date)
        else:
            raise InvalidOperation("wrong ordering mode")
        # query 조립 완료
        return query.count()

    def get_page_no_of_article(self, board_name, heading_name, no, page_length, include_all_headings=True, order_by=LIST_ORDER_ROOT_ID):
        '''
        주어진 게시물이 주어진 방식의 글 목록에서 어느 page 에 있는지 리턴한다.

        @type  board_name: str
        @param board_name: 글을 가져올 게시판의 이름
        @type  heading_name: str
        @param heading_name: 목록에서 보여줄 선택된 말머리
        @type  no: int
        @param no: 글 번호
        @type  page_length: int
        @param page_length: 페이지당 글 갯수
        @type  include_all_headings: bool
        @param include_all_headings: 모든 말머리를 보여줄 것인지의 여부
        @type  order_by: int
        @param order_by: 정렬 방식 [LIST_ORDER_ROOT_ID, LIST_ORDER_LAST_REPLY_DATE]
        @rtype: int
        @return: 해당 게시물이 있는 page 의 번호
        '''
        session = model.Session()

        # Heading ID, Board ID 를 구한다
        board_id = None
        if board_name != u"":
            board_id = self.engine.board_manager.get_board_id(board_name)

        heading_id = None
        if not include_all_headings and heading_name != u"":
            heading_id = self.engine.board_manager._get_heading_by_boardid(session, board_id, heading_name).id

        # 게시판에 선택된 글 이후 게시된 글의 갯수를 센다
        remaining_article_count = self._get_remaining_article_count(session, board_id, heading_id, no, include_all_headings, order_by)

        session.close()
        return (remaining_article_count / page_length) + 1

    @require_login
    @log_method_call
    def article_list_below(self, session_key, board_name, heading_name, no, page_length=20, include_all_headings=True):
        '''
        어떤 게시물의 하단에 표시될 게시물 목록을 구한다.

        @type  session_key: str
        @param session_key: 사용자 Login Session
        @type  board_name: str
        @param board_name: 게시판 이름
        @type  heading_name: string
        @param heading_name: 가져올 글의 글머리 이름
        @type  no: int
        @param no: 글 번호
        @type  page_length: int
        @param page_length: 한 페이지당 표시되는 게시물의 수
        @type  include_all_headings: bool
        @param include_all_headings: 모든 글머리의 글을 가져올지에 대한 여부
        @rtype: ttypes.ArticleList
        @return:
            1. 목록 가져오기 성공: Article List
            2. 목록 가져오기 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        # 사용자 정보 조회
        user_id = self.engine.login_manager.get_user_id_wo_error(session_key)
        listing_mode = self.engine.member_manager.get_listing_mode(user_id)

        # 페이지 정보 조회
        page = self.get_page_no_of_article(board_name, heading_name, no, page_length, include_all_headings, listing_mode)

        # 게시물 목록 조회
        article_list, last_reply_ids = self.get_article_list(board_name, heading_name, page, page_length, include_all_headings, listing_mode)
        self.put_user_specific_info(user_id, article_list, last_reply_ids)

        return article_list

    @require_login
    @log_method_call_important
    def vote_article(self, session_key, board_name, article_no, positive_vote=True):
        '''
        DB의 게시물 하나를 추천하거나 반대함

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  board_name: string
        @param board_name: BBS Name (u"" 을 주면 모든 게시판에 대하여)
        @type  article_no: int
        @param article_no: Article No
        @type  positive_vote: bool
        @param positive_vote: 추천/반대 여부
        @rtype: void
        @return:
            1. 추천 성공: Nothing
            2. 추천 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 로그인되지 않은 유저: InvalidOperation Exception
                3. 데이터베이스 오류: InrernalError Exception
        '''

        session = model.Session()
        board_id = None
        if smart_unicode(board_name) !=  u"":
            board_id = self.engine.board_manager.get_board_id(board_name)
        article = self._get_article(session, board_id, article_no)
        user = self.engine.member_manager._get_user_by_session(session, session_key)
        vote_unique_check_query = session.query(model.ArticleVoteStatus)
        if board_id:
            vote_unique_check_query = vote_unique_check_query.filter_by(user_id=user.id, board_id=board_id, article_id = article.id)
        else:
            vote_unique_check_query = vote_unique_check_query.filter_by(user_id=user.id, article_id = article.id)
        vote_unique_check = vote_unique_check_query.count()
        if vote_unique_check:
            session.close()
            raise InvalidOperation('ALREADY_VOTED')
        else:
            if positive_vote:
                article.positive_vote += 1
            else:
                article.negative_vote += 1
            vote = model.ArticleVoteStatus(user, article.board, article)
            session.add(vote)
            session.commit()
            session.close()

    @require_login
    @log_method_call_important
    def write_article(self, session_key, board_name, article_dic):
        '''
        DB에 게시글 하나를 작성함

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  board_name: string
        @param board_name: BBS Name
        @type  article_dic: ttypes.WrittenArticle
        @param article_dic: Article Dictionary
        @rtype: int
        @return:
            1. Write 성공: Article Number
            2. Write 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 로그인되지 않은 유저: InvalidOperation Exception
                3. 읽기 전용 보드: InvalidOperation Exception
                4. 데이터베이스 오류: InternalError Exception
        '''

        user_ip = self.engine.login_manager.get_user_ip(session_key)

        session = model.Session()
        author = self.engine.member_manager._get_user_by_session(session, session_key)
        board = self.engine.board_manager._get_board_from_session(session, board_name)
        if not board.read_only:
            # 만약 익명 게시판이면, 6시간 이내에 글을 썼으면 안된다
            if board.type == BOARD_TYPE_ANONYMOUS:
                last_article = self.get_article_list_by_username(author.username).filter_by(board_id=board.id).order_by(model.Article.id.desc()).first()
                time_to_filter = datetime.datetime.fromtimestamp(time.time() - 21600)   # 6 Hours
                if last_article is not None and last_article.last_modified_date >= time_to_filter:
                    raise InvalidOperation('Cannot write article until %s' % (last_article.last_modified_date + datetime.timedelta(seconds = 21600)))

            # 글에 적합한 heading 객체를 찾는다
            heading = None
            heading_str = smart_unicode(article_dic.heading)
            if heading_str != u"":
                heading = self.engine.board_manager._get_heading(session, board, heading_str)
            new_article = model.Article(board,
                                        heading,
                                        smart_unicode(article_dic.title),
                                        smart_unicode(article_dic.content),
                                        author,
                                        user_ip,
                                        None)
            session.add(new_article)
            if 'is_searchable' in article_dic.__dict__:
                if not article_dic.is_searchable:
                    new_article.is_searchable = False
            if board.type == BOARD_TYPE_ANONYMOUS:
                new_article.is_searchable = False

            session.commit()
            id = new_article.id
            new_article.last_reply_id  = id
            session.commit()
            session.close()
        else:
            session.close()
            raise InvalidOperation('READ_ONLY_BOARD')
        return id

    @require_login
    @log_method_call_important
    def write_reply(self, session_key, board_name, article_no, reply_dic):
        '''
        댓글 하나를 해당하는 글에 추가

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  board_name: string
        @param board_name: BBS Name
        @type  article_no: int
        @param article_no: Article No in which the reply will be added
        @type  reply_dic: ttypes.WrittenArticle
        @param reply_dic: Reply Dictionary
        @rtype: string
        @return:
            1. 작성 성공: Article Number
            2. 작성 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 존재하지 않는 게시물: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 데이터베이스 오류: InternalError Exception
        '''
        user_ip = self.engine.login_manager.get_user_ip(session_key)

        session = model.Session()
        board_id = None
        author = self.engine.member_manager._get_user_by_session(session, session_key)
        if smart_unicode(board_name) != u'':
            board_id = self.engine.board_manager.get_board_id(board_name)
        article = self._get_article(session, board_id, article_no)
        board_name = article.board.board_name
        board = self.engine.board_manager._get_board_from_session(session, board_name)
        heading = None
        if smart_unicode(board_name) != u'':
            heading_str = smart_unicode(reply_dic.heading)
            if heading_str != u"":
                heading = self.engine.board_manager._get_heading(session, board, heading_str)
        
        new_reply = model.Article(board,
                                heading,
                                smart_unicode(reply_dic.title),
                                smart_unicode(reply_dic.content),
                                author,
                                user_ip,
                                article)
        # XXX 2010.06.17.
        # 현재 root 글에 대해서만 정보를 저장할 것인가
        # 아니면 중간 중간에 걸쳐 있는 글에 대해서도 정보를 저장할 것인가
        # 고민이 필요하다. 즉 parent 들을 추적을 할까 말까에 대해서 ...
        article.reply_count += 1
        article.last_reply_date = new_reply.date
        if article.root:
            article.root.reply_count += 1
            article.root.last_reply_date = new_reply.date

        session.add(new_reply)
        session.commit()
        id = new_reply.id
        new_reply.last_reply_id = id
        article.last_reply_id = id
        if article.root:
            article.root.last_reply_id = new_reply.id
        session.commit()
        if board.type == BOARD_TYPE_ANONYMOUS:
            new_reply.is_searchable = False
        session.commit()

        # hook for notification
        # 1. hook for parent reply author
        my_user_id = self.engine.login_manager.get_user_id(session_key)
        if my_user_id != article.author.id:
            self.engine.noti_manager._add_noti(article.author.id,
                                               board_name, id, new_reply.root.id,
                                               new_reply.root.title, new_reply.author_nickname)

        # 2. hook for subscribed users
        if new_reply.root:
            self.engine.noti_manager._publish(my_user_id,
                                             board_name, id, new_reply.root.id,
                                             new_reply.root.title, new_reply.author_nickname)

        session.close()

        return id

    @require_login
    @log_method_call_important
    def modify_article(self, session_key, board_name, no, article_dic):
        '''
        DB의 해당하는 게시글 수정

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  board_name: string
        @param board_name: 게시판 이름
        @type  no: int
        @param no: Article Number
        @type  article_dic: ttypes.WrittenArticle
        @param article_dic: Article Dictionary
        @rtype: string
        @return:
            1. Modify 성공: Article Number
            2. Modify 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 수정 권한이 없음: InvalidOperation Exception
                5. 데이터베이스 오류: InternalError Exception 
        '''

        board_id = self.engine.board_manager.get_board_id(board_name)
        session = model.Session()
        author_id = self.engine.login_manager.get_user_id(session_key)
        article = self._get_article(session, board_id, no)
        if article.deleted == True:
            session.close()
            raise InvalidOperation("NO_PERMISSION")
        if article.author_id == author_id:
            article.title = smart_unicode(article_dic.title)
            article.content = smart_unicode(article_dic.content)
            # 필요한 경우에만 heading 수정
            new_heading = smart_unicode(article_dic.heading)
            cond1 = article.heading == None
            cond2 = new_heading == u''
            cond = not (cond1 and cond2)
            if not cond1:
                cond = (article.heading.heading != new_heading)
            if cond:
                heading = None
                if not cond2:
                    heading = self.engine.board_manager._get_heading_by_boardid(session, board_id, new_heading)
                article.heading = heading
            article.last_modified_time = datetime.datetime.fromtimestamp(time.time())
            session.commit()
            id = article.id
            session.close()
        else:
            session.close()
            raise InvalidOperation("NO_PERMISSION")
        return id

    def _modify_nickname_in_article(self, board_name, no, new_nickname):
        '''
        해당 게시글의 닉네임을 변경. Internal use only.

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        @type  board_name: string
        @param board_name: 게시물이 있는 Board 의 이름
        @type  no: int
        @param no: Article 게시물의 번호
        @type  new_nickname: string
        @param new_nickname: New Nickname
        @return:
            1. Modify 성공: Article Number
            2. Modify 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: id 를 return 하는 이유는 무엇일까?
        # TODO: 이미 삭제된 글의 닉네임을 변경하는 것은 막아야 할까?
        board_id = self.engine.board_manager.get_board_id(board_name)
        session = model.Session()
        article = self._get_article(session, board_id, no)
        if article.deleted == True:
            session.close()
            raise InvalidOperation("NO_PERMISSION")

        article.author_nickname = smart_unicode(new_nickname)
        article.last_modified_time = datetime.datetime.fromtimestamp(time.time())
        session.commit()
        id = article.id
        session.close()
        return id

    @require_login
    @log_method_call_important
    def modify_nickname_in_article(self, session_key, board_name, no, new_nickname):
        '''
        사용자가 SYSOP일 경우 해당하는 게시글의 닉네임을 변경할 수 있도록 함.

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        @type  board_name: string
        @param board_name: 게시물이 있는 Board 의 이름
        @type  no: int
        @param no: Article 게시물의 번호
        @type  new_nickname: string
        @param new_nickname: New Nickname
        @return:
            1. Modify 성공: Article Number
            2. Modify 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인 되지 않은 유저거나 시삽이 아닐 경우: InvalidOperation Exception
                4. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: SYSOP 체크는 member_manager 에게 넘기자
        # TODO: author 가 아니라 user
        session = model.Session()
        author = self.engine.member_manager._get_user_by_session(session, session_key)
        if not author.is_sysop:
            session.close()
            raise InvalidOperation("NO_PERMISSION")
        session.close()
        return self._modify_nickname_in_article(board_name, no, new_nickname)

    def _modify_bot_nickname_in_article(self, board_name, no, new_nickname):
        '''
        BOT이 해당하는 게시글의 닉네임을 변경할 수 있도록 함. BOT 만 사용할 것.

        @type  board_name: string
        @param board_name: 게시물이 있는 Board 의 이름
        @type  no: int
        @param no: Article 게시물의 번호
        @type  new_nickname: string
        @param new_nickname: New Nickname
        @return:
            1. Modify 성공: Article Number
            2. Modify 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: BOT 인지 검사는 어떻게 할까
        # TODO: TEST 구현
        return self._modify_nickname_in_article(board_name, no, new_nickname)

    def _move_article(self, session, article, new_board_id):
        '''
        @type  session: SQLAlchemy Session
        @param session: 현재 사용중인 SQLAlchemy Session
        @type  article_id: model.Article
        @param article_id: 속한 Board  를 바꿀 게시물의 객체
        @type  new_board_id: int
        @param new_board_id: 해당 게시물이 새롭게 속하게 될 Board 의 고유 id
        '''
        if article.board_id != new_board_id:
            # 글이 속한 Board 를 변경
            article.board_id = new_board_id

            # 글에 대한 Vote Status 의 Board 정보 변경
            try:
                vote_status_queries = session.query(model.ArticleVoteStatus).filter_by(article_id=article.id)
                for query in vote_status_queries:
                    query.board_id = new_board_id
            except InvalidRequestError:
                pass

            # 해당 글에 대한 첨부 File 에 대한 Board 정보 변경
            try:
                file_queries = session.query(model.File).filter_by(article_id=article.id)
                for query in file_queries:
                    query.board_id = new_board_id
            except InvalidRequestError:
                pass

    @require_login
    @log_method_call_important
    def move_article(self, session_key, board_name, no, board_to_move):
        '''
        사용자가 (일단) SYSOP일 경우 해당글을 다른 게시판에 속하도록 옮길수 있게 함.

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        @type  board_name: string
        @param board_name: 게시물이 있는 Board 의 이름
        @type  no: int
        @param no: Article 게시물의 번호
        @type  board_to_move: string
        @param board_to_move: 게시물이 옮겨질 Board 이름.
        @rtype: int
        @return:
            1. Modify 성공: 게시물의 번호 (no 파라메터를 그대로)
            2. Modify 실패:
                1. 유저가 시삽이 아닐 경우: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 데이터베이스 오류: InternalError Exception

        '''
        # TODO: board_name == board_to_move 일 때는?

        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('no permission')

        # Phase 1. 게시물의 이동에 앞서 board id 를 준비
        board_id = self.engine.board_manager.get_board_id(board_name)
        new_board_id = self.engine.board_manager.get_board_id(board_to_move)

        # Phase 2. Article 객체 얻어오기
        session = model.Session()
        article = self._get_article(session, board_id, no)
        self._move_article(session, article, new_board_id)

        if article.reply_count:
            replies = session.query(model.Article).filter_by(root_id=article.id).all()
            for reply in replies:
                self._move_article(session, reply, new_board_id)

        try:
            session.commit()
        except ConcurrentModificationError: # 가장 나옴직한 예외상황 ...
            session.rollback()
            session.close()
            raise InvalidOperation("Database Error")
        session.close()
        return no

    @require_login
    @log_method_call_important
    def delete_article(self, session_key, board_name, no):
        '''
        DB에 해당하는 글 삭제
        
        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  board_name: string
        @param board_name: BBS Name
        @type  no: int
        @param no: Article Number
        @rtype: bool
        @return:
            1. Delete 성공: True
            2. Delete 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 수정 권한이 없음: InvalidOperation Exception
                5. 데이터베이스 오류: InternalError Exception
        '''

        session = model.Session()
        author = self.engine.member_manager._get_user_by_session(session, session_key)
        if board_name != u"":
            board_id = self.engine.board_manager.get_board_id(board_name)
            article = self._get_article(session, board_id, no)
        else:
            article = self._get_article(session, None, no)
        if article.author_id == author.id or author.is_sysop:
            if article.deleted:
                session.close()
                raise InvalidOperation("ALREADY_DELETED")
            article.deleted = True
            article.last_modified_time = datetime.datetime.fromtimestamp(time.time())
            # root 가 있으면 root 의 댓글 수를 1 줄이면서 동시에 destroy 해버린다.
            if article.root:
                article.root.reply_count -= 1
                if article.root.reply_count == 0 and article.root.deleted:
                    article.root.destroyed = True
            # 스스로가 root 이고 reply 달렸던 것이 없으면 destroy 해버린다.
            elif article.reply_count == 0:
                article.destroyed = True
            session.commit()
            session.close()
        else:
            session.close()
            raise InvalidOperation("NO_PERMISSION")
        return True

    def _destroy_article(self, board_id, no):
        '''
        주어진 글을 destroy 한다. destroy 된 글은 아예 글 목록에서 보이지 않게 된다.

        @type  board_id: int
        @param board_id: 해당 게시물이 있는 board id
        @type  no: int
        @param no: 해당 게시물의 id
        '''
        session = model.Session()
        article = self._get_article(session, board_id, no)
        # 이미 destroyed 인 것은 고려할 필요가 없다.
        if article.destroyed:
            session.close()
            raise InvalidOperation("ALREADY_DESTROYED")
        # 현재의 DB 구조상의 한계로 인해, root가 아닌 글은 체크할 수 없다.
        if article.root == None and article.reply_count == 0:
            if article.deleted:
                # 이런 경우에만 일단 destroyed 를 set 해준다.
                article.destroyed = True
                session.commit()
            else:
                raise InvalidOperation("NOT_DELETED")
        else:
            session.close()
            raise InvalidOperation("NOT_IMPLEMENTED")
        session.close()

    @require_login
    @log_method_call_important
    def destroy_article(self, session_key, board_name, no):
        '''
        주어진 글이 Destroy 할만한 글인지 판단하여, 만일 그렇다면 Destroy 함.
        
        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  board_name: string
        @param board_name: BBS Name
        @type  no: int
        @param no: Article Number
        @rtype: void
        @return:
            1. Delete 성공: void
            2. Delete 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 수정 권한이 없음: InvalidOperation Exception
                5. 데이터베이스 오류: InternalError Exception
                6. 기타 : 이 주석은 전부 뜯어고쳐야 함.
        '''

        session = model.Session()
        user = self.engine.member_manager._get_user_by_session(session, session_key)
        session.close()
        # 시삽만 이 작업을 할 수 있다.
        if user.is_sysop:
            board_id = self.engine.board_manager.get_board_id(board_name)
            self._destroy_article(board_id, no)
        else:
            raise InvalidOperation("NO_PERMISSION")

    @require_login
    @log_method_call_important
    def change_article_heading(self, session_key, board_name, original_heading_name, new_heading_name):
        '''
        original_heading에 속한 모든 글의 heading을 new_heading으로 변경한다. 

        @type  session_key: string
        @param session_key: Login session(must to be sysop)
        @type  board_name: string
        @param board_name: 말머리가 속한 게시판의 이름
        @type  original_heading_name: string
        @param original_heading_name: 원래 말머리 이름
        @type  new_heading_name: string
        @param new_heading_name: 새 말머리 이름
        @rtype: void
        @return:
            1. 성공: void
            2. 실패
                1. 로그인되지 않은 유저 : NotLoggedIn()
                2. 시삽이 아닌 경우 : InvalidOperation('no permission')
                3. 존재하지 않는 게시판 : InvalidOperation('board does not exist')
                4. 존재하지 않는 말머리 : InvalidOperation('heading not exist')
        '''
        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('no permission')

        session = model.Session()
        # SQLAlchemy 세션에서 board와 heading 객체를 가져온다. 
        board = self.engine.board_manager._get_board_from_session(session, board_name)
        original_heading = self.engine.board_manager._get_heading(session, board, original_heading_name)
        new_heading = self.engine.board_manager._get_heading(session, board, new_heading_name) 
        try:
            articleList = session.query(model.Article).filter_by(board = board, heading = original_heading).all()
            for article in articleList:
                article.heading = new_heading
            session.commit()
            session.close()
        except:
            session.close()
            raise

    def _fix_article_concurrency(self, board_id, no):
        '''
        주어진 글의 reply 갯수를 바로잡고 last_reply_date 또한 바로잡는다.

        @type  board_id: int
        @param board_id: 게시물이 있는 board 의 id
        @type  no: int
        @param no: 게시물의 번호
        '''
        session = model.Session()
        article = session.query(model.Article).options(eagerload('children')).filter_by(id=no).one()

        if article.root != None:
            session.close()
            raise InvalidOperation("NOT_IMPLEMENTED")

        last_reply_id   = article.id
        last_reply_date = article.last_modified_date
        reply_count     = 0
        # 주어진 글을 순회하며, 실제 reply count, last_reply_id, last_reply_date 구한다.
        stack = []
        stack.append(article)
        while stack:
            art = stack.pop()
            for child in art.children[::-1]:
                if not child.deleted:
                    reply_count += 1
                    if last_reply_id < child.id:
                        last_reply_id = child.id
                    if last_reply_date < child.last_reply_date:
                        last_reply_date = child.last_reply_date
                stack.append(child)

        try:
            if article.reply_count != reply_count:
                article.reply_count = reply_count
            if (not article.destroyed) and article.deleted and (article.reply_count == 0):
                article.destroyed = True
            if article.last_reply_id != last_reply_id:
                article.last_reply_id = last_reply_id
            if article.last_reply_date != last_reply_date:
                article.last_reply_date = last_reply_date

            session.commit()
            session.close()

        except InvalidRequestError:
            session.rollback()
            session.close()
            raise InvalidOperation("Internal Error")

    @require_login
    @log_method_call_important
    def fix_article_concurrency(self, session_key, board_name, no):
        '''
        주어진 글의 concurrency 가 올바른지 확인.
        올바르지 않다면 이를 고침.
        
        @type  session_key: string
        @param session_key: 사용자 Login Session (시삽이어야 함)
        @type  board_name: string
        @param board_name: BBS Name
        @type  no: int
        @param no: Article Number
        @rtype: void
        @return:
            1. Fix 성공: void
            2. Fix 실패:
                1. 존재하지 않는 게시물번호: InvalidOperation Exception
                2. 존재하지 않는 게시판: InvalidOperation Exception
                3. 로그인되지 않은 유저: InvalidOperation Exception
                4. 수정 권한이 없음: InvalidOperation Exception
                5. 데이터베이스 오류: InternalError Exception
                6. 기타 : 이 주석은 전부 뜯어고쳐야 함.
        '''

        session = model.Session()
        user = self.engine.member_manager._get_user_by_session(session, session_key)
        session.close()
        # 시삽만 이 작업을 할 수 있다.
        if user.is_sysop:
            board_id = self.engine.board_manager.get_board_id(board_name)
            self._fix_article_concurrency(board_id, no)
        else:
            session.close()
            raise InvalidOperation("NO_PERMISSION")

    def _get_last_article_no(self):
        '''
        현재 존재하는 글 중 가장 마지막 글의 글 번호를 반환
        글이 없을 경우 None을 반환

        @rtype:  integer
        @return:
            1. 글 존재 : integer
            2. 글이 하나도 없을 때 : None
        '''

        session = model.Session()
        r = session.query(func.max(model.Article.id))[0][0]
        session.close()
        return r

    @require_login
    @log_method_call_important
    def scrap_article(self, session_key, article_no):
        '''
        주어진 글을 스크랩함

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  article_no: int
        @param article_no: 글 번호

        @rtype:  void
        @return: None
        '''
        session = model.Session()
        article = self._get_article(session, u'', article_no)
        user = self.engine.member_manager._get_user_by_session(session, session_key)
        scrap_check_query = session.query(model.ScrapStatus).filter_by(user_id=user.id, article_id=article.id)
        scrap_check = scrap_check_query.count()

        if scrap_check:
            session.close()
            raise InvalidOperation('ALREADY_SCRAPPED')
        else:
            new_scrap = model.ScrapStatus(user, article)
            session.add(new_scrap)
            session.commit()
            session.close()

    @require_login
    @log_method_call_important
    def unscrap_article(self, session_key, article_no):
        '''
        주어진 글을 스크랩 취소함

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  article_no: int
        @param article_no: 글 번호

        @rtype:  void
        @return: None
        '''
        session = model.Session()
        article = self._get_article(session, u'', article_no)
        user = self.engine.member_manager._get_user_by_session(session, session_key)
        scrap_check_query = session.query(model.ScrapStatus).filter_by(user_id=user.id, article_id=article.id)
        scrap_check = scrap_check_query.count()

        if not scrap_check:
            session.close()
            raise InvalidOperation('NOT_SCRAPPED')
        else:
            session.delete(scrap_check_query.one())
            session.commit()
            session.close()

    @log_method_call
    def scrapped_article_list(self, session_key, page=1, page_length=20):
        '''
        스크랩 된 게시물 목록 읽어오기. 모든 보드에서 읽어오므로 board나 heading에 관한 옵션은 따로 필요치 않다.
        Thrift 형식의 Article 객체 리스트를 반환한다

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  page: integer
        @param page: Page Number to Request
        @type  page_length: integer
        @param page_length: Count of Article on a Page
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: Article List
            2. 리스트 읽어오기 실패:
                1. 존재하지 않는 게시판: InvalidOperation Exception
                2. 페이지 번호 오류: InvalidOperation Exception
                3. 데이터베이스 오류: InternalError Exception
        '''
        # TODO : 여기에도 LIST_ORDERED_BY.. 형태를 적용시킬 수 있을까? 또, 그게 굳이 필요할까?
        # TODO: 상당 부분 get_article_list 혹은 article_list들과 겹치는데, 잘 리팩토링하면 합칠 수 있을 듯.

        if page == 0: page = 1

        session = model.Session()
        # Part 1. list<ScrapStatus> 형태의 객체 받아오기
        user = self.engine.member_manager._get_user_by_session(session, session_key)
        scrap_status_list = session.query(model.User).filter_by(id=user.id).one().scrapped_articles
        article_count = len(scrap_status_list)

        # Part 2. 페이지번호 관련 정보 구하기
        try:
            last_page, offset, last = self.get_page_info(article_count, page, page_length)
        except ValueError as e:
            session.close()
            if str(e) == 'WRONG_PAGENUM':
                raise InvalidOperation(str(e))
            else:
                raise

        # Part 3. 목록을 정렬한 후 list<Article>화 한다
        scrap_status_list.sort(key=lambda stat: stat.article_id, reverse=True)
        scrap_status_list = scrap_status_list[offset:last]
        article_list = [stat.article for stat in scrap_status_list]

        session.close()

        # Part 4. 게시물의 목록, 마지막 답글 번호 목록 정리
        last_reply_ids = [article.last_reply_id for article in article_list]
        article_list   = [Article(**self._get_dict(article, LIST_ARTICLE_WHITELIST)) for article in article_list]
        article_list   = ArticleList(hit=article_list, current_page=page, last_page=last_page, results=article_count)

        # Part 5. 이런저런 정보를 부착
        self.put_user_specific_info(user.id, article_list, last_reply_ids)

        return article_list

    @log_method_call
    def scrapped_article_list_below(self, session_key, no, page_length=20):
        '''
        스크랩 된 게시물을 읽을 때 밑에 표시될 게시글 목록을 가져오는 함수이다.
        Thrift 형식의 Article 객체 리스트를 반환한다

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  no: integer
        @param no: Article No
        @type  page_length: integer
        @param page_length: Count of Article on a Page
        @rtype: list
        @return:
            1. 리스트 읽어오기 성공: Article List
            2. 리스트 읽어오기 실패:
                1. 페이지 번호 오류: InvalidOperation Exception
                2. 데이터베이스 오류: InternalError Exception
        '''
        # TODO: 더 General한 Form으로 바꿀 수 있을 것이다

        session = model.Session()
        # Part 1. list<ScrapStatus> 형태의 객체 받아오기
        user = self.engine.member_manager._get_user_by_session(session, session_key)
        scrap_status_list = session.query(model.User).filter_by(id=user.id).one().scrapped_articles
        session.close()

        # Part 2. article id만 뽑아서 정렬
        scrap_status_list = [x.article_id for x in scrap_status_list]
        scrap_status_list.sort(reverse=True)

        article_count = len(scrap_status_list)
        if article_count == 0:
            raise InvalidOperation("WRONG_ARTICLE_NUMBER")

        # Part 3. 총 페이지 수 계산
        total_page = (article_count + page_length - 1) / page_length

        # Part 4. 적당한 쪽 번호를 계산 ( Binary Search )
        low, high, page = (1, total_page, 1)
        while low <= high:
            mid = (low + high) / 2
            _, offset, _ = self.get_page_info(article_count, mid, page_length)
            if scrap_status_list[offset] >= no:
                page = mid
                low = mid + 1
            else:
                high = mid - 1

        # Part 5. 가져온다.
        return self.scrapped_article_list(session_key, page, page_length)

    @require_login
    @log_method_call_important
    def register_notice(self, session_key, article_id):
        '''
        사용자가 SYSOP일 경우 해당 게시물을 공지로 만듬

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        @type  article_id: int
        @param article_id: Article 게시물의 번호
        @rtype: void
        @return:
            1. 성공: void
            2. 실패:
                1. 권한 없음 : InvalidOperation Exception
                2. 이미 공지임 : InvalidOperation Exception
                3. 기타 : InternalError Exception
        '''
        session = model.Session()
        author = self.engine.member_manager._get_user_by_session(session, session_key)
        if not author.is_sysop:
            session.close()
            raise InvalidOperation("NO_PERMISSION")

        try:
            article = session.query(model.Article).filter_by(id=article_id).one()
        except NoResultFound:
            session.close()
            raise InvalidOperation("ARTICLE NOT EXISTS")
        except MultipleResultsFound:
            session.close()
            raise InternalError()

        try:
            notice = session.query(model.BoardNotice).filter_by(article_id=article_id).one()
            session.close()
            raise InvalidOperation("ALREADY IN NOTICE")
        except NoResultFound:
            notice = model.BoardNotice(article=article)
            session.add(notice)
            session.commit()

        session.close()

    @require_login
    @log_method_call_important
    def unregister_notice(self, session_key, article_id):
        '''
        사용자가 SYSOP일 경우 해당 게시물을 공지에서 내림

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        @type  article_id: int
        @param article_id: Article 게시물의 번호
        @rtype: void
        @return:
            1. 성공: void
            2. 실패:
                1. 권한 없음 : InvalidOperation Exception
                2. 이미 공지 아님 : InvalidOperation Exception
                3. 기타 : InternalError Exception
        '''
        session = model.Session()
        author = self.engine.member_manager._get_user_by_session(session, session_key)
        if not author.is_sysop:
            session.close()
            raise InvalidOperation("NO_PERMISSION")

        try:
            article = session.query(model.Article).filter_by(id=article_id).one()
        except NoResultFound:
            session.close()
            raise InvalidOperation("ARTICLE NOT EXISTS")
        except MultipleResultsFound:
            session.close()
            raise InternalError()

        try:
            notice = session.query(model.BoardNotice).filter_by(article_id=article_id).one()
        except NoResultFound:
            session.close()
            raise InvalidOperation("NOT A NOTICE")

        session.delete(notice)
        session.commit()
        session.close()

    @log_method_call
    def notice_list(self, board_name):
        '''
        게시판의 공지 목록을 가져옴

        @type  board_name: string
        @param board_name: 게시판 이름
        @rtype: list<ttypes.ArticleList>
        @return: 게시물 목록
        '''

        session = model.Session()
        board = self.engine.board_manager.get_board(board_name)
        notices = session.query(model.BoardNotice).join(model.BoardNotice.article).filter(model.Article.board_id==board.id)
        notices = [Article(**self._get_dict(article.article, LIST_ARTICLE_WHITELIST)) for article in notices]
        notices = ArticleList(hit=notices, current_page=1, last_page=1, results=len(notices))

        return notices

    @log_method_call
    def recent_article_list(self, board_name, count=5):
        '''
        게시판의 최근 글 count개를 가져옴

        @type  board_name: string
        @param board_name: 게시판 이름
        @rtype: list<ttypes.Article>
        @return: 게시물 목록
        '''

        session = model.Session()
        basic_query = self._get_basic_query(session, board_name, None, True)
        ordered_query = self._get_ordered_query(session, basic_query, LIST_ORDER_ROOT_ID)

        article_dict_list = self._get_dict_list(ordered_query[:count], RECENT_ARTICLE_WHITELIST)
        session.close()

        return [Article(**article) for article in article_dict_list]

    __public__ = [
            get_today_best_list,
            get_today_best_list_specific,
            get_weekly_best_list,
            get_weekly_best_list_specific,
            get_today_most_list,
            get_today_most_list_specific,
            get_weekly_most_list,
            get_weekly_most_list_specific,
            article_list,
            read_article,
            read_recent_article,
            article_list_below,
            vote_article,
            write_article,
            write_reply,
            modify_article,
            modify_nickname_in_article,
            move_article,
            delete_article,
            destroy_article,
            fix_article_concurrency,
            get_page_no_of_article,
            scrap_article,
            unscrap_article,
            scrapped_article_list,
            scrapped_article_list_below,
            register_notice,
            unregister_notice,
            notice_list,
            recent_article_list]

# vim: set et ts=8 sw=4 sts=4
