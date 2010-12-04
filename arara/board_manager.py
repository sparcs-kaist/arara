# -*- coding: utf-8 -*-
from sqlalchemy.exceptions import InvalidRequestError, IntegrityError
from arara import model
from arara.model import BOARD_TYPE_NORMAL, BOARD_TYPE_PICTURE
from arara.util import filter_dict, require_login
from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara.util import smart_unicode, datetime2timestamp

from arara_thrift.ttypes import *

log_method_call = log_method_call_with_source('board_manager')
log_method_call_important = log_method_call_with_source_important('board_manager')

BOARD_MANAGER_WHITELIST = ('board_name', 'alias', 'board_description', 'read_only', 'hide', 'id', 'headings', 'order', 'category_id', 'type', 'to_read_level', 'to_write_level')

CATEGORY_WHITELIST = ('category_name', 'id', 'order')

USER_QUERY_WHITELIST = ('username', 'nickname', 'email',
        'signature', 'self_introduction', 'campus', 'last_login_ip', 'last_logout_time')

class BoardManager(object):
    '''
    보드 추가 삭제 및 관리 관련 클래스
    '''

    def __init__(self, engine):
        '''
        @type  engine: ARAraEngine
        '''
        self.engine = engine
        #added category list and dict, cache function
        self.all_category_list = None
        self.all_category_dict = None
        self.cache_category_list()
        # Internal Cache!
        self.all_board_list = None
        self.all_board_dict = None
        self.all_board_and_heading_list = None
        self.all_board_and_heading_dict = None
        self.cache_board_list()
        # Integrated category & board list
        self.all_category_and_board_list = None
        self.all_category_and_board_dict = None
        self.cache_category_and_board_list()
        # Integrity Check
        self._check_integrity()

    def _check_integrity(self):
        '''
        엔진이 기동될 때 최초 1회 실행.
        '''
        # TODO: 속도 향상을 위해 query 를 order 와 deleted 에 대해서만 뽑아오거나 하기
        session = model.Session()
        try:
            # 게시판들 중 deleted 가 아니면서 order 가 존재하지 않는 게시판이 있다면
            # 관리자가 직접 DB 수정을 해야 한다.
            boards = session.query(model.Board).all()
            for board in boards:
                assert board.deleted or board.order != None
            # 카테고리의 경우에는 무조건 order 가 존재해야 한다.
            categories = session.query(model.Category).all()
            for category in categories:
                assert category.order != None
        except Exception:
            session.close()
            raise
        session.close()

    def _get_dict(self, item, whitelist=None):
        '''
        @type  item: model.Board / model.Category
        @param item: dictionary 로 바꿀 객체 (여기서는 Board 나 Category)
        @type  whitelist: list
        @param whitelist: dictionary 에 남아있을 필드의 목록
        @rtype: dict
        @return: item 에서 whitelist 에 있는 필드만 남기고 적절히 dictionary 로 변환한 결과물
        '''
        item_dict = item.__dict__
        if whitelist:
            filtered_dict = filter_dict(item_dict, whitelist)
        else:
            filtered_dict = item_dict
        return filtered_dict

    def _get_dict_list(self, raw_list, whitelist=None):
        '''
        @type  raw_list: iterable(list, generator)<model.Article / model.Category>
        @param raw_list: _get_dict 에 통과시키고 싶은 대상물의 모임
        @type  whitelist: list<string>
        @param whitelist: _get_dict 에 넘겨줄 whitelist
        @rtype: list<dict(whitelist filtered)>
        @return: _get_dict 를 통과시킨 raw_list 의 원소들로 구성된 list
        '''
        # TODO: generator 화
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist)
            return_list.append(filtered_dict)
        return return_list

    def _is_sysop(self, session_key):
        '''
        @type  session_key: string
        @param session_key: 사용자 Login Session
        '''
        # TODO: member manager 로 옮기기
        if not self.engine.member_manager.is_sysop(session_key):
            raise InvalidOperation('no permission')

    def _add_category(self, category_name):
        '''
        카테고리를 실제로 추가한다. Internal use only.

        @type  category_name: string
        @param category_name: name of category
        @rtype: void
        @return: 
            1.성공 : 없음
            2.오류가 있을 경우 InvalidOperation

        '''
        # TODO: category_name 에 공백 문자 금지
        # TODO: 좀더 다양한 예외상황에 대한 처리
        session = model.Session()
        # 모든 category 는 cache 되어 있으므로 category 의 수에 1 더한 값이 새 order 가 됨
        category_order = len(self.all_category_list) + 1
        category_to_add = model.Category(smart_unicode(category_name), category_order)
        try:
            session.add(category_to_add)
            session.commit()
            session.close()
        except IntegrityError:
            session.rollback()
            session.close()
            raise InvalidOperation('already added')
        # 새로운 카테고리가 추가되었으므로 cache 를 update 한다
        self.cache_category_list()

    @require_login
    @log_method_call_important
    def add_category(self, session_key, category_name):
        '''
        카테고리를 추가한다.

        @type  session_key: string
        @param session_key: 사용자 Login Session (시삽이어야 함)
        @type  category_name: string
        @param category_name: name of category
        @rtype: void
        @return: 
            1.성공 : 없음
            2.오류가 있을 경우 InvalidOperation

        '''
        self._is_sysop(session_key)
        self._add_category(category_name)

    @log_method_call
    def _add_bot_category(self, category_name):
        '''
        BOT 이 직접 카테고리를 추가한다. BOT 에 의해서만 호출되어야 한다.

        @type  category_name: string
        @param category_name: name of category
        @rtype: void
        @return: 
            1.성공 : 없음
            2.오류가 있을 경우 InvalidOperation
        '''
        # TODO: BOT Manager 내부에서만 호출하는 것을 좀 다른 방식으로 보장해보자
        self._add_category(category_name)

    def _get_last_board_order_until_category(self, category_name):
        '''
        주어진 이름의 category 의 가장 뒤에 있는 board 의 순서를 돌려준다.

        @type  category_name: string
        @param category_name: 카테고리의 이름
        @rtype: int
        @return: 해당 category 의 가장 뒤에 있는 board 의 순서
        '''
        if category_name == None:
            board_count = 0
            if len(self.all_category_and_board_dict[None]) == 0:
                # category name 이 있는 보드들 뿐이므로 그 보드의 갯수가 곧 order 가 된다
                board_count = len(self.all_board_list)
                return board_count
            else:
                # category 가 없는 board 들 중 마지막 것으로 하면 된다
                board_count = self.all_category_and_board_dict[None][-1].order
                return board_count
        else:
            board_count = 0
            if len(self.all_category_and_board_dict[category_name]) == 0:
                # 선택한 category 까지의 board 들의 갯수를 계속 더한다
                for category in self.all_category_list:
                    if category.category_name == category_name:
                        break
                    else:
                        board_count += len(self.all_category_and_board_dict[category.category_name])
                return board_count
            else:
                # 선택한 category 의 board 들 중 마지막 것으로 하면 된다.
                board_count = self.all_category_and_board_dict[category_name][-1].order
                return board_count

    def _add_board(self, board_name, alias, board_description, heading_list, category_name, board_type, to_read_level, to_write_level):

        '''
        보드를 신설한다. 내부 사용 전용.

        @type  session_key: string
        @param session_key: 사용자 Login Session (시삽이어야 함)
        @type  board_name: string
        @param board_name: 개설할 Board Name
        @type  board_description: string
        @param board_description: 보드에 대한 한줄 설명
        @type  heading_list: list<string>
        @param heading_list: 보드에 존재할 말머리 목록 (초기값 : [] 아무 말머리 없음)
        @type  category_name: string
        @param category_name: 보드가 속하는 카테고리의 이름(초기값 : None 카테고리 없음)
        @type  board_type: int
        @param board_type: 보드의 종류 (0 : 일반 게시판, 1 : 사진 게시판)
        @type  to_read_level: int
        @param to_read_level: 게시판 글을 읽기위해 필요한 authentication_mode 레벨 (초기값: 3 포탈인증자 읽기 가능)
        @type  to_write_level: int
        @param to_write_level: 게시판 글을 쓰기위해 필요한 authenticatino_mode 레벨 (초기값: 3 포탈인증자 쓰기 가능)
        @rtype: boolean, string 
        @return:
            1. 성공: None
            2. 실패:
                1. 로그인되지 않은 유저: 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: 'no permission'
                3. 존재하는 게시판: 'board already exist'
                4. 데이터베이스 오류: 'DATABASE_ERROR'

        '''
        # TODO: 존재않는 Category 를 집어넣을 때에 대한 대처
        # TODO: board_order 를 좀 더 깔끔하게 구하기
        session = model.Session()
        board_order = self._get_last_board_order_until_category(category_name) + 1
        # board order 와 같거나 뒤에 있던 모든 board 의 순서를 재조정한다.
        boards = session.query(model.Board).filter(model.Board.order != None).order_by(model.Board.order)[board_order - 1:]
        # TODO: for문을 돌리지 않고 query 한큐에 해결할 수는 없을까?
        for board in boards:
            board.order += 1

        category = None
        if category_name != None:
            category = self._get_category_from_session(session, category_name)
        board_to_add = model.Board(smart_unicode(board_name), alias, board_description, board_order, category, board_type, to_read_level, to_write_level)
        try:
            session.add(board_to_add)
            # Board Heading 들도 추가한다.
            # TODO: heading 에 대한 중복 검사가 필요하다. (지금은 따로 없다)
            for heading in heading_list:
                board_heading = model.BoardHeading(board_to_add, smart_unicode(heading))
                session.add(board_heading)
            session.commit()
            session.close()
        except IntegrityError:
            session.rollback()
            session.close()
            raise InvalidOperation('already added')
        # 보드에 변경이 발생하므로 캐시 초기화
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def add_board(self, session_key, board_name, alias, board_description, heading_list = [], category_name = None, board_type = BOARD_TYPE_NORMAL, to_read_level = 3, to_write_level = 3):

        '''
        보드를 신설한다.

        @type  session_key: string
        @param session_key: 사용자 Login Session (시삽이어야 함)
        @type  board_name: string
        @param board_name: 개설할 Board Name
        @type  board_description: string
        @param board_description: 보드에 대한 한줄 설명
        @type  heading_list: list<string>
        @param heading_list: 보드에 존재할 말머리 목록 (초기값 : [] 아무 말머리 없음)
        @type  category_name: string
        @param category_name: 보드가 속하는 카테고리의 이름(초기값 : None 카테고리 없음)
        @type  board_type: int
        @param board_type: 보드의 종류 (0 : 일반 게시판, 1 : 사진 게시판)
        @type  to_read_level: int
        @param to_read_level: 게시판 글을 읽기위해 필요한 authentication_mode 레벨 (초기값: 3 포탈인증자 읽기 가능)
        @type  to_write_level: int
        @param to_write_level: 게시판 글을 쓰기위해 필요한 authenticatino_mode 레벨 (초기값: 3 포탈인증자 쓰기 가능)
        @rtype: void
        @return:
            1. 성공: None
            2. 실패:
                1. 로그인되지 않은 유저: 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: 'no permission'
                3. 존재하는 게시판: 'board already exist'
                4. 데이터베이스 오류: 'DATABASE_ERROR'

        '''
        # TODO: 위의 "실패" 주석 제대로 정리하기
        self._is_sysop(session_key)
        self._add_board(board_name, alias, board_description, heading_list, category_name, board_type, to_read_level, to_write_level)

    def _add_bot_board(self, board_name, board_description = '', heading_list = [], hide = True, category_name = None, board_type = BOARD_TYPE_NORMAL, to_read_level = 3, to_write_level = 3):
        '''
        BOT용 보드를 신설한다.
        주의 : 이 함수는 BOT Manager에서만 사용되어야 한다

        @type  board_name: string
        @param board_name: 개설할 Board Name
        @type  board_description: string
        @param board_description: 보드에 대한 한줄 설명 (초기값 : '' Description 없음)
        @type  heading_list: list<string>
        @param heading_list: 보드에 존재할 말머리 목록 (초기값 : [] 아무 말머리 없음)
        @type  hide: Boolean
        @param hide: 게시판을 숨길지의 여부. (초기값 : True, 숨김)
        @type  category_name: string
        @param category_name: 보드가 속한 카테고리 이름 (초기값 : None 카테고리 없음)
        @type  board_type: int
        @param board_type: 보드의 종류 (0 : 일반 게시판, 1 : 사진 게시판)
        @type  to_read_level: int
        @param to_read_level: 게시판 글을 읽기위해 필요한 authentication_mode 레벨 (초기값: 3 포탈인증자 읽기 가능)
        @type  to_write_level: int
        @param to_write_level: 게시판 글을 쓰기위해 필요한 authenticatino_mode 레벨 (초기값: 3 포탈인증자 쓰기 가능)
        @rtype: void
        @return:
            1. 성공: None
            2. 실패:
                1. 존재하는 게시판: 'board already exist'
                2. 데이터베이스 오류: 'DATABASE_ERROR'
        '''
        # TODO: 위의 "실패" 주석 제대로 정리
        self._add_board(board_name, board_name, board_description, heading_list, category_name, board_type, to_read_level, to_write_level)
        if hide:
            self._hide_board(board_name)
            # 보드에 변경이 발생하므로 캐시 초기화
            self.cache_board_list()
    
    def _get_board(self, board_name):
        '''
        Cache 되어 있는 board 를 가져온다.

        @type  board_name: string
        @param board_name: 가져올 board 이름
        @rtype: ttypes.Board
        @return: 해당 board 의 객체
        '''
        try:
            return self.all_board_dict[smart_unicode(board_name)]
        except KeyError:
            raise InvalidOperation('board does not exist')
        return board

    def _get_board_from_session(self, session, board_name):
        '''
        DB 로부터 주어진 이름의 board 에 대한 정보를 읽어들인다.

        @type  session: SQLAlchemy Session
        @param session: 사용할 Session
        @type  board_name: string
        @param board_name: 불러올 게시판의 이름
        @rtype: model.Board
        @return:
            1. 성공시 - 찾고자 하는 Board 에 대한 SQLAlchemy Board 객체
            2. 실패시
                1. 존재하지 않는 게시판 : InvalidOperation('board does not exist')
        '''
        try:
            board = session.query(model.Board).filter_by(board_name=smart_unicode(board_name)).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('board does not exist')
        return board

    def _get_category(self, category_name):
        '''
        Cache 되어 있는 Category 를 가져온다.

        @type  category_name: string
        @param category_name: 불러올 카테고리의 이름
        @rtype: ttypes.Category
        @return:
            1. 성공 : 찾고자 하는 Thrift Category 객체
            2. 실패 : 존재하지 않는 카테고리 : InvalidOperation('category does not exist')
        '''
        try:
            return self.all_category_dict[smart_unicode(category_name)]
        except KeyError:
            raise InvalidOperation('category does not exist')
        return category

    def _get_category_from_session(self, session, category_name):
        '''
        DB 로부터 주어진 이름의 category 에 대한 정보를 읽어들인다.
        Internal Use Only.

        @type  session: SQLAlchemy Session
        @param session: 사용할 Session
        @type  category_name: string
        @param category_name: 불러올 카테고리 이름
        @rtype: model.Category
        @return:
            1. 성공시 - 찾고자 하는 Category 에 대한 SQLAlchemy category 객체
            2. 실패시
                1. 존재하지 않는 게시판 : InvalidOperation('category does not exist')
        '''
     
        try:
            category = session.query(model.Category).filter_by(category_name=smart_unicode(category_name)).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('category does not exist')
        return category

    @log_method_call
    def get_board(self, board_name):
        '''
        보드 하나에 대한 자세한 정보를 얻는다.

        @type  board_name: string
        @param board_name: 찾고자 하는 board 의 이름
        @rtype: ttypes.Board
        '''
        # TODO: board cache 구조 대개편
        return self._get_board(smart_unicode(board_name))

    @log_method_call
    def get_board_id(self, board_name):
        '''
        주어진 이름의 게시판의 id 를 찾는다.

        @type  board_name: string
        @param board_name: id 를 찾고자 하는 게시판의 이름
        @rtype: int
        @return: 1. 찾고자 한 게시판의 id
                 2. 실패시 - InvalidOperatino('board does not exist')
        '''
        return self._get_board(board_name).id

    @log_method_call
    def get_category(self, category_name):
        '''
        주어진 이름의 카테고리를 찾는다.

        @type  category_name: string
        @param category_name: 찾고자 하는 카테고리의 이름
        @rtype: ttypes.Category
        @return: 1. 성공- 찾고자 한 Thrift Category 객체
                 2. 실패- InvalidOperation('category does not exist')
        '''
        
        return self._get_category(category_name)

    @log_method_call
    def get_category_id(self, category_name):
        '''
        주어진 이름의 카테고리의 id 를 찾는다.

        @type  board_name: string
        @param board_name: id 를 찾고자 하는 카테고리의 이름
        @rtype: int
        @return: 1. 찾고자 한 카테고리의 id
                 2. 실패시 - InvalidOperation('category does not exist')
        '''

        return self._get_category(category_name).id

    @require_login
    @log_method_call_important
    def add_board_heading(self, session_key, board_name, heading_name):
        '''
        주어진 게시판에 새로운 말머리를 추가한다.

        @type  session_key: string
        @param session_key: 사용자 Login Sesson (SYSOP)
        @type  board_name: string
        @param board_name: 말머리가 추가될 대상 게시판의 이름
        @type  heading_name: string
        @param heading_name: 추가될 말머리 이름
        @rtype: None
        @return: 1. 성공- None
                 2. 실패
                    1. 로그인되지 않은 유저 : NotLoggedIn()
                    2. 시삽이 아닌 경우 : InvalidOperation('no permission')
                    3. 존재하지 않는 게시판 : InvalidOperation('board does not exist')
                    4. 이미 존재하는 말머리 : InvalidOperation('heading already exists in board')
        '''
        # TODO: 위에서 말하는 것과 같은 error message 를 돌려주도록 수정
        self._is_sysop(session_key)

        session = model.Session()
        # 이미 해당 말머리가 존재하는지 검사한다. 
        board = self._get_board_from_session(session, board_name)
        if session.query(model.BoardHeading).filter_by(board = board).filter_by(heading = heading_name).count() != 0:
            session.close()
            raise InvalidOperation('heading \'%s\' already exists in board \'%s\'' % (heading_name, board_name))
        # 말머리를 추가한다. 
        try:
            new_heading = model.BoardHeading(board, smart_unicode(heading_name))
            session.add(new_heading)
            session.commit()
            session.close()
        except:
            session.rollback()
            session.close()
            raise InternalError("unknown error")
            
    @require_login
    @log_method_call_important
    def delete_board_heading(self, session_key, board_name, heading_name, new_heading_name = ''):
        '''
        주어진 게시판의 주어진 말머리에 속해 있던 글은 모두 새로운 말머리로 이동시키고 해당 말머리를 삭제한다.  
        
        @type  session_key: string
        @param session_key: 사용자 Login Sesson (SYSOP)
        @type  board_name: string
        @param board_name: 삭제될 말머리가 속한 게시판의 이름
        @type  heading_name: string
        @param heading_name: 삭제될 말머리 이름
        @rtype: None
        @return: 1. 성공- None
                 2. 실패
                    1. 로그인되지 않은 유저 : NotLoggedIn()
                    2. 시삽이 아닌 경우 : InvalidOperation('no permission')
                    3. 존재하지 않는 게시판 : InvalidOperation('board does not exist')
                    4. 존재하지 않는 말머리 : InvalidOperation('heading not exist')
        '''
        self._is_sysop(session_key)

        self.engine.article_manager.change_article_heading(session_key, board_name, heading_name, new_heading_name)

        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        heading = self._get_heading(session, board, heading_name)
        try:
            session.delete(heading)
            session.commit()
            session.close()
        except:
            session.rollback()
            session.close()
            raise
        
    @log_method_call
    def get_board_heading_list_fromid(self, board_id):
        '''
        주어진 board의 heading 의 목록을 가져온다. 단 board_id 를 이용한다.

        @type  board_id: int
        @param board_id: heading 을 가져올 보드의 id
        @rtype : list<string>
        @return: heading 의 목록
        '''
        # TODO: board_heading_list 를 좀 더 파이썬스럽게 만들기
        session = model.Session()
        board_heading_list = []
        heading_query = session.query(model.BoardHeading).filter_by(board_id=board_id)
        heading_result = heading_query.all()

        for board_heading in heading_result:
            board_heading_list.append(board_heading.heading)
        session.close()

        return board_heading_list

    @log_method_call
    def get_board_heading_list(self, board_name):
        '''
        cache 로부터 주어진 board의 heading 의 목록을 가져온다.
        주의 : internal cache 에 영향을 받으므로 internal cache 를 생성하는 중에는 사용하면 안 된다.

        @type  board_name: string
        @param board_name: heading 을 가져올 보드의 이름
        @rtype : list<string>
        @return: heading 의 목록
        '''
        board_id = self.get_board_id(smart_unicode(board_name))
        return self.get_board_heading_list_fromid(board_id)

    @log_method_call
    def get_board_type(self, board_name):
        '''
        주어진 board의 type을 돌려준다.

        @type  board_name: string
        @param board_name: type을 돌려줄 board의 이름
        @rtype : integer
        @return: type을 나타내는 integer
        '''

        return self._get_board(board_name).type

    def cache_category_list(self):
        '''
        DB 로부터 category 목록을 읽어들여 cache 를 생성한다.
        '''
        # TODO: 이 또한 좀더 깔끔하게 Python 스럽게 고칠 수 있다.
        session = model.Session()
        categories = session.query(model.Category).order_by(model.Category.order).all()
        category_dict_list = self._get_dict_list(categories, CATEGORY_WHITELIST)
        session.close()

        self.all_category_list = [Category(**d) for d in category_dict_list]
        self.all_category_dict = {}
        for category in self.all_category_list:
            self.all_category_dict[category.category_name] = category

        self.cache_category_and_board_list()

    def cache_board_list(self):
        '''
        DB 로부터 board 목록을 읽어들여 cache 를 생성한다.
        '''
        # TODO: 이 또한 좀더 깔끔하게 Python 스럽게 고칠 수 있다.
        session = model.Session()
        boards = session.query(model.Board).filter_by(deleted=False).order_by(model.Board.order).all()
        board_dict_list = self._get_dict_list(boards, BOARD_MANAGER_WHITELIST)
        session.close()
        # Board Heading 도 전부 가져온다.
        for each_board in board_dict_list:
            each_board['headings'] = self.get_board_heading_list_fromid(each_board['id'])
        # all_board_list 와 all_board_dict 로 만든다. 
        self.all_board_list = [Board(**d) for d in board_dict_list]
        self.all_board_dict = {}
        for board in self.all_board_list:
            self.all_board_dict[board.board_name] = board

        self.cache_category_and_board_list()

    def cache_category_and_board_list(self):
        '''
        DB 로부터 Category 별 Board 목록을 읽어들여 cache 를 생성한다.
        즉, all_category_and_board_dict 는 키가 category 이름이고
        value 가 board 의 list 인 녀석이 된다.
        '''
        session = model.Session()
        categories = session.query(model.Category).order_by(model.Category.order).all()
        category_dict_list = self._get_dict_list(categories, CATEGORY_WHITELIST)

        self.all_category_and_board_list = []
        self.all_category_and_board_dict = {}

        for category in category_dict_list:
            category_name = category['category_name']
            category_id   = category['id']

            boards = session.query(model.Board).filter_by(deleted=False).filter_by(category_id=category_id).order_by(model.Board.order).all()
            board_dict_list = self._get_dict_list(boards, BOARD_MANAGER_WHITELIST)
            board_list = [Board(**d) for d in board_dict_list]

            self.all_category_and_board_dict[category_name] = board_list
            self.all_category_and_board_list.append(board_list)

        # Category 가 None 인 board 들도 챙겨준다
        boards = session.query(model.Board).filter_by(deleted=False).filter_by(category=None).order_by(model.Board.order).all()
        board_dict_list = self._get_dict_list(boards, BOARD_MANAGER_WHITELIST)
        board_list = [Board(**d) for d in board_dict_list]
        
        self.all_category_and_board_dict[None] = board_list
        self.all_category_and_board_list.append(board_list)

        # 끝.
        session.close()

    def _get_heading(self, session, board, heading):
        '''
        cache로부터 주어진 heading 객체를 찾아낸다.

        @type  session: SQLAlchemy Session object
        @param session: 현재 사용중인 session
        @type  board: model.Board
        @param board: 선택된 게시판 object
        @type  heading: unicode string
        @param heading: 선택한 말머리
        @rtype : model.BoardHeading
        @return:
            1. 선택된 BoardHeading 객체 (단, heading == u"" 일 때는 None)
            2. 실패:
        '''
        heading = smart_unicode(heading)
        if heading == u"":
            return None
        try:
            return session.query(model.BoardHeading).filter_by(board=board, heading=heading).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('heading not exist')

    def _get_heading_by_boardid(self, session, board_id, heading):
        '''
        주어진 heading 객체를 찾아낸다. 단 board_id 를 이용한다.

        @type  session: SQLAlchemy Session object
        @param session: 현재 사용중인 session
        @type  board_id: Board id
        @param board_id: 선택된 게시판의 id
        @type  heading: unicode string
        @param heading: 선택한 말머리
        @rtype : model.BoardHeading
        @return:
            1. 선택된 BoardHeading 객체 (단, heading == u"" 일 때는 None)
            2. 실패:
        '''
        heading = smart_unicode(heading)
        if heading == u"":
            return None
        try:
            return session.query(model.BoardHeading).filter_by(board_id=board_id, heading=heading).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('heading not exist')

    @log_method_call
    def get_board_list(self):
        '''
        cache 가 있다면 cache 된 board_list, 를 그렇지 않다면 cache 를 생성하고 리턴한다.
        '''
        if self.all_board_list == None:
            self.cache_board_list()
        return self.all_board_list

    @log_method_call
    def get_category_list(self):
        '''
        cache 가 있다면 cache 된 category_list, 를 그렇지 않다면 cache 를 생성하고 리턴한다.
        '''
        if self.all_category_list == None:
            self.cache_category_list()
        return self.all_category_list


    @require_login
    @log_method_call_important
    def add_read_only_board(self, session_key, board_name):
        '''
        보드를 읽기 전용으로 변경해주는 함수

        @type  session_key: string
        @param session_key: 사용자 Login Sesson (SYSOP)
        @type  board_name: string
        @param board_name: Board Name
        @rtype: void
        @return:
            1. 읽기전용 성공: void
            2. 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: False, 'no permission'
                3. 존재하지 않는 게시판: False, 'board does not exist'
                4. 이미 읽기전용인 보드의 경우: False, 'ALEARDY_READ_ONLY_BOARD'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        self._is_sysop(session_key)

        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        if board.read_only:
            session.close()
            raise InvalidOperation('aleardy read only board')
        board.read_only = True
        session.commit()
        session.close()
        # 보드에 변경이 발생하므로 캐시 초기화
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def return_read_only_board(self, session_key, board_name):
        '''
        보드를 읽기 전용에서 다시 쓰기/읽기 가능 보드로 변경해주는 함수

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        @type  board_name: string
        @param board_name: Board Name
        @rtype: void
        @return:
            1. 성공: void
            2. 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: False, 'no permission'
                3. 존재하지 않는 게시판: False, 'board does not exist'
                4. 이미 읽기전용가 아닌경우 보드의 경우: False, 'not read only board'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''

        self._is_sysop(session_key)
        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        if not board.read_only:
            session.close()
            raise InvalidOperation('not read only board')
        board.read_only = False
        session.commit()
        session.close()
        # 보드에 변경이 발생하므로 캐시 초기화
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def change_board_order(self, session_key, board_name, new_order):
        """
        보드의 순서를 바꾼다. 카테고리의 범위를 넘어서지 않는 선에서.

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        @type  board_name: string
        @param board_name: 순서를 변경할 보드의 이름
        @type  new_order: int
        @param new_order: 보드가 표시될 순서
        @rtype: void
        @return:
            1. 성공: None
            2. 실패:
                1. 로그인되지 않은 유저: 'NOT_LOGGEDIN'
                2. 시삽이 아닌 경우: 'no permission'
                3. 존재하지 않는 게시판: 'board does not exist'
                4. 순서를 지정할 수 없는 게시판: 'invalid board'
                5. 잘못된 순서(범위 초과): 'invalid order'
                6. 데이터베이스 오류: 'DATABASE_ERROR'
        """

        self._is_sysop(session_key)
        session = model.Session()

        board_name = smart_unicode(board_name)
        current_board = self._get_board_from_session(session, board_name)
        if current_board.order == None:
            session.close()
            raise InvalidOperation('invalid board')

        board_list = session.query(model.Board).filter_by(category=current_board.category).filter(model.Board.order != None).order_by(model.Board.order).all()
        if not board_list[0].order <= new_order <= board_list[-1].order:
            session.close()
            raise InvalidOperation('invalid order')

        if new_order < current_board.order:
            for board in board_list:
                if new_order <= board.order < current_board.order:
                    board.order += 1
        elif new_order > current_board.order:
            for board in board_list:
                if current_board.order < board.order <= new_order:
                    board.order -= 1

        #현재 보드의 order를 new_order로 변경한다. 
        current_board.order = new_order

        try:
            session.commit()
        except InvalidRequestError: # TODO: 이게 날 가능성이 있는지 고민해보자
            session.close()
            raise InternalError("DATABASE ERROR")

        session.close()
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def edit_category(self, session_key, category_name, new_category_name):
        '''
        카테고리의 이름을 변경한다.

        @type  session_key: string
        @param session_key: 사용자 로그인 Session
        @type  category_name: string
        @param category_name: 변경할 카테고리의 이름
        @type  new_category_name: string
        @param new_category_name: 카테고리의 새 이름
        @rtype: void
        @return:
            1.성공 : 아무것도 리턴하지 않음
            2.실패 : 이미 있는 카테고리의 이름일 경우 InvalidOperation(category already exists)
                     
        '''
        self._is_sysop(session_key)
        category_name = smart_unicode(category_name)
        new_category_name = smart_unicode(new_category_name)

        session = model.Session()
        category = self._get_category_from_session(session, category_name)
        category.category_name = new_category_name

        try:
            session.commit()
            session.close()
        except IntegrityError:
            raise InvalidOperation("category already exists")
        except InvalidRequestError: # TODO: 어떤 경우에 이렇게 되나?
            raise InternalError()
        self.cache_category_list()

    @require_login
    @log_method_call_important
    def change_category_order(self, session_key, category_name, new_order):
        '''
        카테고리의 순서를 변경한다.

        @type  session_key: string
        @param session_key: 사용자 로그인 Session
        @type  category_name: string
        @param category_name: 변경할 카테고리의 이름
        @type  new_order: int
        @param new_order: 카테고리의 새로운 순서
        @rtype: void
        @return:
            1.성공 : 아무것도 리턴하지 않음
            2.실패 : 잘못된 범위의 경우 InvalidOperation('invalid order')
        '''
        self._is_sysop(session_key)
        # 올바른 order 인지 검사
        if not 0 < new_order <= len(self.all_category_list):
            raise InvalidOperation('invalid order')

        session = model.Session()
        current_category = self._get_category_from_session(session, category_name)
        board_list = session.query(model.Board).filter(model.Board.order != None).order_by(model.Board.order).all()
        category_list = session.query(model.Category).order_by(model.Category.order).all()

        if new_order < current_category.order :
            board_offset = len(self.all_category_and_board_dict[current_category.category_name])
            new_board_offset = 0
            # 순서가 뒤로 밀리는 category 에 속하는 board 들을 뒤로 밀기
            for board in board_list:
                if board.category != None:
                    if new_order <= board.category.order < current_category.order:
                        board.order += board_offset
                        new_board_offset += 1
            # 위로 올라가는 category 에 속하는 board 들을 앞으로 당기기
            for board in board_list:
                if board.category != None:
                    if board.category.category_name == current_category.category_name:
                        board.order -= new_board_offset
            # category 들간의 위치 조정
            for category in category_list:
                if new_order <= category.order < current_category.order:
                    category.order += 1
        elif category.order < new_order:
            board_offset = len(self.all_category_and_board_dict[current_category.category_name])
            new_board_offset = 0
            # 순서가 위로 끌려오는 category 에 속하는 board 들을 앞으로 끌기
            for board in board_list:
                if board.category != None:
                    if current_category.order < board.category.order <= new_order:
                        board.order -= board_offset
                        new_board_offset += 1
            # 뒤로 밀리는 category 에 속하는 board 들을 뒤로 밀기
            for board in board_list:
                if board.category != None:
                    if board.category.category_name == current_category.category_name:
                        board.order += new_board_offset
            # category 들간의 위치 조정
            for category in category_list:
                if current_category.order < category.order <= new_order:
                    category.order -= 1

        current_category.order = new_order
        try:
            session.commit()
            session.close()
        except InvalidRequestError: #TODO: 어떤 경우에 이렇게 되나??
            session.rollback()
            session.close()
            raise InvalidOperation('DATABASE Error?')

        self.cache_category_list()
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def change_auth(self, session_key, board_name, read_level, write_level):
        '''
        보드의 사용자 접근 권한 설정을 바꾼다.
        @type  session_key: string
        @param session_key: 시삽의 session key
        @type  board_name: string
        @param board_name: 선택된 게시판
        @type  read_level: int (1~3)
        @param read_level: 새로 설정된 읽기 권한
        @type  write_level: int (1~3)
        @param write_level: 새로 설정된 쓰기 권한

        '''
        self._is_sysop(session_key)
        board_id = self.get_board_id(board_name)

        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        board.to_read_level = read_level
        board.to_write_level = write_level
        try:
            session.commit()
        except:
            session.rollback()
        session.close()
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def edit_board(self, session_key, board_name, new_name, new_alias, new_description, new_category_name=None):
        '''
        보드의 이름과 설명을 변경한다. 이름이나 설명을 바꾸고 싶지 않으면 파라메터로 길이가 0 인 문자열을 주면 된다.

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        @type  board_name: string
        @param board_name: 설명을 수정하고자 하는 Board Name
        @type  new_name: string
        @param new_name: 보드에게 할당할 새 이름 (미변경시 '')
        @type  new_description: string
        @param new_description: 보드에게 할당할 새 설명 (미변경시 '')
        @type  new_category_name: string
        @param new_category_name: 보드에게 할당할 새 카테고리 (미변경시 값을 주지 않음. 초기값 None)
        @rtype: void
        @return:
            1. 성공: 아무것도 리턴하지 않음
            2. 실패:
                1. 로그인되지 않은 유저: 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: 'no permission'
                3. 존재하지 않는 게시판: 'board does not exist'
                4. 기타 오류 : 주석 추가해 주세요
        '''
        # XXX (2010.12.05)
        # Category 가 할당되어 있던 보드에 Category 를 지우려면 어째야 할까.
        # XXX end
        self._is_sysop(session_key)

        board_name = smart_unicode(board_name)
        new_name = smart_unicode(new_name)
        new_alias = smart_unicode(new_alias)
        new_description = smart_unicode(new_description)
        if new_category_name != None: # 파라메터로 주어지지 않았을 때
            new_category_name = smart_unicode(new_category_name)

        # 변경이 필요한 항목에 대해서만 변경을 진행한다.
        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        if new_name != u'':
            board.board_name = new_name
        if new_alias != u'':
            board.alias = new_alias
        if new_description != u'':
            board.board_description = new_description
        if new_category_name != None:
            board.category = self._get_category_from_session(session, new_category_name)

        try:
            session.commit()
            session.close()
        except IntegrityError:
            raise InvalidOperation("board already exist")
        # TODO :전체적인 Error 들 정리 ...
        except InvalidRequestError:
            raise InternalError()
        # 보드에 변경이 생겼으므로 캐시 초기화
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def change_board_category(self, session_key, board_name, new_category_name):
        '''
        보드의 Category 를 변경한다.
        사실은 edit_board 에 대한 Wrapper 이다.

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        @type  board_name: string
        @param board_name: Category를 변경하고자 하는 Board Name
        @type  new_category_name: string
        @param new_category_name: 보드에게 할당할 새 카테고리
        @rtype: void
        @return:
            1. 성공: 아무것도 리턴하지 않음
            2. 실패:
                1. 로그인되지 않은 유저: 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: 'no permission'
                3. 존재하지 않는 게시판: 'board does not exist'
                4. 기타 오류 : 주석 추가해 주세요
        '''
        self.edit_board(session_key, board_name, u"", u"", u"", new_category_name)

    def _hide_board(self, board_name):
        '''
        보드를 숨겨주는 진짜 함수. 내부 사용 전용.
        @type  board_name: string
        @param board_name: Board Name
        @rtype: void
        @return:
            1. 성공: void
            2. 실패:
                1. 존재하지 않는 게시판: InvalidOperation('board does not exist')
                2. 이미 숨겨져 있는 보드의 경우: InvalidOperation('already hidden')
                3. 데이터베이스 오류: InternalError('DATABASE_ERROR')
        '''
        # TODO: 주석대로 Exception 뱉니?
        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        if board.hide:
            session.close()
            raise InvalidOperation('already hidden')
        board.hide = True
        session.commit()
        session.close()
        # 보드에 변경이 발생하므로 캐시 초기화
        self.cache_board_list()

    @require_login
    @log_method_call_important
    def hide_board(self, session_key, board_name):
        '''
        보드를 숨겨주는 함수

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        @type  board_name: string
        @param board_name: Board Name
        @rtype: void
        @return:
            1. 성공: void
            2. 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: False, 'no permission'
                3. 존재하지 않는 게시판: False, 'board does not exist'
                4. 이미 숨겨져 있는 보드의 경우: False, 'already hidden'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        self._is_sysop(session_key)
        self._hide_board(board_name)

    @require_login
    @log_method_call_important
    def return_hide_board(self, session_key, board_name):
        '''
        숨겨진 보드를 다시 보여주는 함수

        @type  session_key: string
        @param session_key: User Key
        @type  board_name: string
        @param board_name: Board Name
        @rtype: void
        @return:
            1. 성공: void
            2. 실패:
                1. 로그인되지 않은 유저: False, 'NOT_LOGGEDIN'
                2. 시샵이 아닌 경우: False, 'no permission'
                3. 존재하지 않는 게시판: False, 'board does not exist'
                4. 숨겨져 있는 보드가 아닌 경우: False, 'not hidden board'
                5. 데이터베이스 오류: False, 'DATABASE_ERROR'
        '''
        self._is_sysop(session_key)
        session = model.Session()
        board = self._get_board_from_session(session, board_name)
        if not board.hide:
            session.close()
            raise InvalidOperation('not hidden board')
        board.hide = False
        session.commit()
        session.close()
        # 보드에 변경이 발생하므로 캐시 초기화
        self.cache_board_list()


    @require_login
    @log_method_call_important
    def delete_category(self, session_key, category_name):
        '''
        카테고리를 삭제하는 함수
        삭제된 카테고리에 속해있던 보드들의 카테고리는 None이 된다.

        @type  session_key : string
        @param session_key : 사용자 Login Session (SYSOP)
        @type  category_name : string
        @param category_name : 삭제할 카테고리의 이름
        @rtype : void
        @return :
            1. 성공: 리턴 안함
            2. 실패: InvalidOperation(category does not exist)
        '''
        # TODO: Category 를 삭제할 경우 Category Ordering 에 문제가 생길 수 있다.
        # 카테고리 삭제시 기존 Category 들의 ordering 을 재조정하는 함수가 필요.

        self._is_sysop(session_key)
        session = model.Session()
        category = self._get_category_from_session(session, category_name)
        for board in session.query(model.Board).filter_by(category=category).all():
            board.category = None
        session.delete(category)
        session.commit()
        session.close()
        self.cache_category_list()

    @require_login
    @log_method_call_important
    def delete_board(self, session_key, board_name):
        '''
        주어진 게시판을 삭제 처리한다.

        @type  session_key : string
        @param session_key : 사용자 Login Session (SYSOP)
        @type  category_name : string
        @param category_name : 삭제할 보드의 이름
        '''
        # TODO: hide 와 delete 의 차이는 ?
        self._is_sysop(session_key)
        session = model.Session()
        board = self._get_board_from_session(session, smart_unicode(board_name))

        if board.order != None:
            self.change_board_order(session_key, board_name, session.query(model.Board).filter(model.Board.order != None).count())
            board.order = None

        board.deleted = True
        session.commit()
        session.close()
        # 보드에 변경이 발생하므로 캐시 초기화
        self.cache_board_list()
    
    def has_bbs_manager(self, board_name):
        '''
        게시판에 관리자가 설정 되었는지 여부를 알려준다.
        @type   board_name: string
        @param  board_name: 관리자 유무를 확인할 보드
        @rtype: bool
        @return: bbs_managers table 안에 게시판id와 관리자 id가 등록 되었는지 여부
        '''
        # TODO : 다른 방법은 없나?
        session = model.Session()
        board_id = self.get_board_id(board_name)
        query = session.query(model.BBSManager).filter_by(board_id=board_id)
        try:
            managed_board = query.one()
            session.close()
            return True
        except InvalidRequestError:
            session.close()
            return False

    def _is_already_manager(self, board_id, manager_id):
        '''
        현 게시판에 사용자가 이미 관리자로 지정되있는지 체크한다.
        @type   board_id: int
        @param  board_id: 체크할 게시판 id
        @type   manager_id: int
        @param  manager_id: 체크할 사용자 id
        @rtype: bool
        @return: 사용자가 게시판의 관리자로 지정되있으면 true를 돌려준다.
        '''
        session = model.Session()
        try:
            query = session.query(model.BBSManager).filter_by(board_id=board_id, manager_id=manager_id).one()
            session.close()
            return True
        except InvalidRequestError:
            session.close()
            return False

    @require_login
    def add_bbs_manager(self, session_key, board_name, username):
        '''
        시삽이 각 게시판의 관리자(들) 등록.(한 관리자가 여러 게시판 관리도 가능)
        @type   session_key: string
        @param  session_key: User Key (SYSOP)
        @type   board_name: string
        @param  board_name: 관리자를 지정할 보드
        @type   username: string
        @param  username: 관리자가 될 사용자
        '''
        self._is_sysop(session_key)
        session = model.Session()
        board = session.query(model.Board).filter_by(board_name=board_name).one()
        user = self.engine.member_manager._get_user(session, username)
        if self._is_already_manager(board.id, user.id):
            raise InvalidOperation('User is already a manager for the board.')
        if user.is_sysop:
            raise InvalidOperation('SYSOP does not need to be assigned as manager.')
        # TODO: 내부의 에러 메시지는 장기적으로는 JQuery 쪽에서도 이 에러 메시지를 참고하도록 수정하는 게...
        bbs_manager = model.BBSManager(board, user)
        session.add(bbs_manager)
        session.commit()
        session.close()

    @require_login
    def remove_bbs_manager(self, session_key, board_name, username):
        '''
        더이상 관리자가 아닌 사용자의 게시판 관리자 record를 지운다.
        아직 테스트코드 없음.

        @type   session_key: string
        @param  session_key: 사용자 Login Session
        @type   board_name: string
        @param  board_name: 관리자를 지울 보드
        @type   username: string
        @param  username: 관리자가 아니게 된 사용자

        '''
        self._is_sysop(session_key)
        session = model.Session()
        board = session.query(model.Board).filter_by(board_name=board_name).one()
        user = self.engine.member_manager._get_user(session, username)
        bbs_manager = session.query(model.BBSManager).filter_by(board_id=board.id, manager_id=user.id).one()
        session.delete(bbs_manager)
        session.commit()
        session.close()
   
    def get_bbs_managers(self, board_name):
        '''
        현 게시판 관리자(들)을 return한다.
        프론트엔드에서 게시판 정보도 함께 나타내기 위해 board_name도 포함되어있다.

        @type   board_name: string
        @param  board_name: 관리자를 확인할 게시판
        @rtype: list<PublicUserInformation>
        @return: 보드의 관리자들의 list
        '''
        session = model.Session()
        board_id = self.get_board_id(board_name)
        try:
            bbs_managers = []
            managements = session.query(model.BBSManager).filter_by(board_id=board_id).all()
            for management in managements:
                query = session.query(model.User).filter_by(id=management.manager_id).one()
                manager_dict = filter_dict(query.__dict__, USER_QUERY_WHITELIST)
                if manager_dict['last_logout_time']:
                    manager_dict['last_logout_time'] = datetime2timestamp(manager_dict['last_logout_time'])
                else:
                    manager_dict['last_logout_time'] = 0
                manager = PublicUserInformation(**manager_dict)
                bbs_managers.append(manager)
            session.close()
            return bbs_managers           
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('bbs manager not exist')

    def is_bbs_manager_of(self, session_key, board_name):
        '''
        user session_key 와 보드 이름을 받아서 유저가 어떤 보드의 매니저 인지 체크한다.
        @type   session_key: string
        @param  session_key: 사용자 Login Session
        @type   board_name: string
        @param  board_name: 관리자 체크를 할 보드
        @rtype: bool
        @return: 유저가 그 보드의 관리자이면 true 아니면 false를 리턴.
        '''
        # TODO: user 가져오는 것은 다른 함수로 빼내기 (예외처리를 그 속에서)
        session = model.Session()
        user = self.engine.member_manager._get_user_by_session(session, session_key)
        try:
            board_id = self.get_board_id(board_name)
            bbs_manager = session.query(model.BBSManager).filter_by(board_id=board_id,manager_id=user.id).one()
        except InvalidRequestError:
            session.close()
            return False
        session.close()
        return True
