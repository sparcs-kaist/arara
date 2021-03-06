# -*- coding: utf-8 -*-

import hashlib
import datetime
import time
import logging
import random
import string

from sqlalchemy.exc import InvalidRequestError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import or_, not_, and_

from libs import datetime2timestamp, filter_dict, is_keys_in_dict, smart_unicode
from arara_thrift.ttypes import *
from arara import arara_manager
from arara import model
from arara import ara_memcached
from arara.util import require_login
from arara.util import log_method_call_with_source, log_method_call_with_source_important, log_method_call_with_source_duration
from arara.util import send_mail
import etc.arara_settings
from etc import arara_settings

log_method_call = log_method_call_with_source('member_manager')
log_method_call_duration = log_method_call_with_source_duration('member_manager')
log_method_call_important = log_method_call_with_source_important('member_manager')

import re
PROPER_USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_\-\.]+$')

# KAIST E-Mail Address Restriction
# 계정명 길이 경계값이 4-20 또는 3-20 으로 알려져 있어서, 1씩 여유를 두었다
PROPER_EMAIL_REGEX = re.compile(r'^[0-9a-zA-Z\_\-\.]{2,21}@kaist.(ac.kr|edu)$')

# TODO: non-KAIST E-Mail Address 에 대한 검증도 준비한다

class NoPermission(Exception):
    pass

class WrongPassword(Exception):
    pass

# User Public Keys : 사용자 등록시 필요한 Parameter들이 들어있는 Dict의 형식을 결정. (arara.thrift에서는 UserRegistration)
USER_PUBLIC_KEYS = ['username', 'password', 'nickname', 'email',
        'signature', 'self_introduction', 'default_language', 'campus']
# User Query Whitelist : 사용자의 이름, 닉네임 등으로 사용자를 검색할 후 정보를 받을 Dict의 형식을 결정. (arara.thrift에서는 PublicUserInformation)
USER_QUERY_WHITELIST = ('username', 'nickname', 'email',
        'signature', 'self_introduction', 'campus', 'last_login_ip', 'last_logout_time')
# User Public Whitelist : 사용자에 대한 정보를 받을 Dict의 형식을 결정. USER_QUERY_WHITELIST와 달리 현재 로그인 된 회원의 정보를 반환하는 용도로 사용함. (arara.thrift에서는 UserInformation)
USER_PUBLIC_WHITELIST= ('username', 'nickname', 'email', 'last_login_ip',
        'last_logout_time', 'signature', 'self_introduction',
        'default_language', 'campus', 'activated', 'widget', 'layout', 'id', 'listing_mode')
# User Public Modifiable Whitelist : 사용자에 대한 정보 중 수정 가능한 것들의 Dict의 형식을 결정. (arara.thrift에서는 UserModification)
USER_PUBLIC_MODIFIABLE_WHITELIST= ('nickname', 'signature',
        'self_introduction', 'default_language', 'campus', 'widget', 'layout', 'listing_mode')
# User Search Whitelist : 사용자에 대한 검색 결과를 받을 Dict의 형식을 결정. (arara.thrift에서는 SearchUserResult)
USER_SEARCH_WHITELIST = ('username', 'nickname')

class MemberManager(arara_manager.ARAraManager):
    '''
    회원 가입, 회원정보 수정, 회원정보 조회, 이메일 인증등을 담당하는 클래스
    '''

    def __init__(self, engine):
        '''
        @type  engine: ARAraEngine
        '''
        super(MemberManager, self).__init__(engine)
        self._register_sysop()

        if etc.arara_settings.BOT_ENABLED:
            self._register_bot()

    def _register_without_confirm(self, user_reg_dic, is_sysop):
        '''
        confirm 과정 없이 사용자를 활성화된 상태로 등록하는 함수

        @type  user_reg_dic: dict('username', 'password', 'nickname', 'email', 'signature', 'self_introduction', 'default_language', 'campus')
        @param user_reg_dic: User Information
        @type  is_sysop: bool
        @param is_sysop: 유저가 시삽권한을 가질지를 결정
        @rtype: void
        @return:
            1. 사용자 등록이 성공했을 경우 : void
            2. 사용자 등록이 실패했을 경우 : Invalid Operation
        '''
        # TODO: 예외 상황이 여러 가지가 있을 수 있다. DB 자체 에러, 이미 등록된 유저 등. 나누어야 한다.
        try:
            user = model.User(**user_reg_dic)
            session = model.Session()
            session.add(user)
            user.activated = True
            user.is_sysop = is_sysop
            session.commit()
            session.close()
        except:
            session.rollback()
            session.close()
            import traceback
            self.logger.exception("Special Exception : \n%s", traceback.format_exc())
            raise InvalidOperation('Cannot add users without confirm')

    def _register_sysop(self):
        '''
        시삽을 등록하는 함수

        @rtype: void
        @return:
            1. 시삽 등록이 성공했을 경우 : void
            2. 시삽 등록이 실패했을 경우 : InvalidOperation('Cannot add users without confirm')
        '''
        from etc.arara_settings import SYSOP_INITIAL_USERNAME, SYSOP_INITIAL_PASSWORD
        # 이미 시삽이 등록되어 있을 땐 굳이 할 필요가 없다.
        if self.is_registered(SYSOP_INITIAL_USERNAME):
            return

        SYSOP_REG_DIC = {'username' :SYSOP_INITIAL_USERNAME,
                         'password' :SYSOP_INITIAL_PASSWORD,
                         'nickname' :u'SYSOP',
                         'email'    :u'sysop@ara.kaist.ac.kr',
                         'signature':u'--\n아라 BBS 시삽 (SYStem OPerator)',
                         'self_introduction':u'--\n아라 BBS 시삽 (SYStem OPerator)',
                         'default_language':u'ko_KR',
                         'campus': u''}

        self._register_without_confirm(SYSOP_REG_DIC, True)

    def _register_bot(self):
        '''
        BOT용 계정을 등록하는 함수.

        @rtype: void
        @return:
            1. BOT 계정 등록이 성공했을 경우 : void
            2. BOT 계정 등록이 실패했을 경우 : Invalid Operation
        '''
        # TODO: BOT 유저의 e-mail 주소 ....
        from etc.arara_settings import BOT_ACCOUNT_USERNAME, BOT_ACCOUNT_PASSWORD
        # 이미 BOT 계정이 등록되어 있을 땐 굳이 할 필요가 없다
        if self.is_registered(BOT_ACCOUNT_USERNAME):
            return

        BOT_ACCOUNT_DIC = {'username' :BOT_ACCOUNT_USERNAME,
                           'password' :BOT_ACCOUNT_PASSWORD,
                           'nickname' :u'BOT',
                           'email'    :u'bot@ara.kaist.ac.kr',
                           'signature':u'--\n아라 봇(AraBOT)',
                           'self_introduction':u'--\n아라의 각종 서비스를 담당하는 아라봇입니다',
                           'default_language':u'ko_KR',
                           'campus'   : u''}

        self._register_without_confirm(BOT_ACCOUNT_DIC, False)

    @log_method_call
    def logout_process(self, user_id):
        '''
        사용자의 로그아웃 시각을 DB에 기록한다.

        @type  user_id: int
        @param user_id: 로그아웃하고자 하는 사용자의 고유 id
        '''
        # TODO: 사용자 정보 가져오는 쿼리문을 다른 함수로 빼기
        # TODO: Test 구현
        try:
            session = model.Session()
            user = session.query(model.User).filter_by(id=user_id).one()
            user.last_logout_time = datetime.datetime.fromtimestamp(time.time())
            session.commit()
            session.close()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('DATABASE_ERROR')

    def update_last_logout_time(self, user_ids):
        '''
        주어진 사용자들의 로그아웃 타임을 현재 시각으로 갱신한다.
        실존하는 사용자인지는 검사하지 않고 따로 에러도 안 나므로 주의.

        @type  user_ids: list<int>
        @param user_ids: 로그아웃 타임을 갱신하고자 하는 사용자의 id 목록
        '''
        now = datetime.datetime.fromtimestamp(time.time())
        session = model.Session()
        try:
            cond = or_(*[model.User.id == id for id in user_ids])
            session.execute(model.User.__table__.update().values(last_logout_time=now).where(cond))
            session.commit()
            session.close()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('Database Error?')

    def _get_user(self, session, username, errmsg = 'user does not exist'):
        '''
        해당 username 의 사용자에 대한 SQLAlchemy 객체를 리턴한다.
        없으면 적절한 InvalidOperation 을 돌려준다.

        @type  session: SQLAlchemy Session
        @param session: SQLAlchemy Session
        @type  username: string
        @param username: 사용자의 id
        @type  errmsg: string
        @param errmsg: 해당 사용자가 없을 경우 돌려줄 에러 문자열
        @rtype: model.User
        @return:
            1. 사용자가 존재할 경우: 해당 사용자에 대한 객체
            2. 사용자가 존재하지 않을 경우: errmsg 가 포함된 InvalidOperation
        '''
        try:
            user = session.query(model.User).filter_by(username=smart_unicode(username)).filter_by(deleted=False).one()
            return user
        except InvalidRequestError:
            session.close()
            raise InvalidOperation(errmsg)

    def _get_user_by_id(self, session, user_id, close_session = True):
        '''
        해당 user_id 사용자에 대한 SQLAlchemy 객체를 리턴한다.

        @type  session: SQLAlchemy Session
        @param session: SQLAlchemy Session
        @type  user_id: int
        @param user_id: 사용자 내부 id
        @type  close_session: bool
        @param close_session: Exception 발생시 session 을 닫을지의 여부
        @rtype: model.User
        @return:
            1. 사용자가 존재할 경우: 해당 사용자에 대한 객체
            2. 사용자가 존재하지 않을 경우: errmsg 가 포함된 InvalidOperation
        '''
        try:
            user = session.query(model.User).filter_by(id=user_id).filter_by(deleted=False).one()
            return user
        except InvalidRequestError:
            if close_session:
                session.close()
            raise InvalidOperation('user does not exist')

    def _get_user_by_session(self, session, session_key, close_session = True):
        '''
        해당 session_key 로 로그인한 사용자에 대한 SQLAlchemy 객체를 리턴한다.

        @type  session: SQLAlchemy Session
        @param session: SQLAlchemy Session
        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  close_session: bool
        @param close_session: 로그인되지 않은 사용자일 때 session 을 닫을 것인가의 여부 (기본값: True)
        @rtype: model.User
        @return:
            1. 사용자가 존재할 경우: 해당 사용자에 대한 객체
            2. 사용자가 존재하지 않을 경우: errmsg 가 포함된 InvalidOperation
        '''
        try:
            user_id = self.engine.login_manager.get_user_id(session_key)
            return self._get_user_by_id(session, user_id)
        except NotLoggedIn:
            if close_session:
                session.close()
            raise

    def authenticate(self, username, password, user_ip):
        '''
        사용자가 입력한 password 로 검사한다.

        @type  username: string
        @param username: 사용자의 id
        @type  password: string
        @param password: 사용자의 비밀번호
        @type  user_ip: string
        @param user_ip: 사용자의 IP 주소
        '''
        # TODO: user 쿼리 밖으로 빼기
        # TODO: ret 딕셔너리 만드는 코드 다듬기
        # TODO: 궁극적으로 비밀번호 저장방식 바꾸기
        username = smart_unicode(username)
        if username.strip() == u"" or username == u" ":
            raise InvalidOperation('wrong username')
        session = model.Session()
        user = self._get_user(session, username, 'wrong username')
        try:
            if user.compare_password(password):
                if user.activated:
                    current_time = time.time()
                    user.last_login_time = datetime.datetime.fromtimestamp(current_time)
                    user.last_login_ip = unicode(user_ip)
                    ret = {'last_login_time': current_time,
                           'nickname': user.nickname,
                           'id': user.id}
                    if user.lost_password_token:
                        for tok in user.lost_password_token:
                            session.delete(tok)
                    session.commit()
                    session.close()
                    return AuthenticationInfo(**ret)
                else:
                    session.close()
                    raise InvalidOperation(u'not activated\n%s\n%s' % (user.username, user.nickname))
            else:
                session.close()
                raise InvalidOperation('wrong password')
        except InvalidOperation:
            raise
        except Exception, e:
            self.logger.warning("Exception occur on member_manager.authenticate. username <%s> and Error <%s>" % (username, repr(e)))
            raise InvalidOperation("unexpected error on authentication, contact SYSOP")

    def _get_dict(self, item, whitelist=None):
        '''
        @type  item: model.User
        @param item: dictionary 로 바꿀 객체 (여기서는 사용자)
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
        @type  raw_list: iterable(list, generator)<model.User>
        @param raw_list: _get_dict 에 통과시키고 싶은 대상물의 모임
        @type  whitelist: list<string>
        @param whitelist: _get_dict 에 넘겨줄 whitelist
        @rtype: list<dict(whitelist filtered)>
        @return: _get_dict 를 통과시킨 raw_list 의 원소들의 list
        '''
        # TODO: Generator 화 하지 않을 이유가 없다.
        return_list = []
        for item in raw_list:
            filtered_dict = self._get_dict(item, whitelist)
            return_list.append(filtered_dict)
        return return_list

    @log_method_call
    def register_(self, user_reg_info):
        '''
        DB에 회원 정보 추가. activation code를 발급한다.
        예외상황:
            1. 시샵이 아이디인 경우: InvalidOperation('permission denied')
            2. 이미 가입한 사용자의 경우: InvalidOperation('already added')
            3. 데이터베이스 오류: InternalError('database error')

        @type  user_reg_info: ttypes.UserRegistration
        @param user_reg_info: 사용자의 회원가입 정보를 담은 객체
        @rtype: string
        @return: 사용자 인증코드
        '''
        # TODO: 한글 아이디 허용

        # Smart Unicode 적용
        for keys in USER_PUBLIC_KEYS:
            user_reg_info.__dict__[keys] = smart_unicode(user_reg_info.__dict__[keys])

        # Check if username is proper
        if user_reg_info.username.lower() == etc.arara_settings.SYSOP_INITIAL_USERNAME.lower():
            raise InvalidOperation('permission denied')
        if not PROPER_USERNAME_REGEX.match(user_reg_info.username):
            raise InvalidOperation('username not permitted')
        if not PROPER_EMAIL_REGEX.match(user_reg_info.email):
            raise InvalidOperation('emai other than @KAIST not permitted')

        key = (user_reg_info.username +
            user_reg_info.password + user_reg_info.nickname)
        activation_code = hashlib.md5(key).hexdigest()

        session = model.Session()
        try:
            # Register user to db
            user = model.User(**user_reg_info.__dict__)
            session.add(user)
            # Register activate code to db
            user_activation = model.UserActivation(user, activation_code)
            session.add(user_activation)
            session.commit()
        except IntegrityError:
            session.rollback()
            session.close()
            raise InvalidOperation('already added')
        except InvalidRequestError:
            session.rollback()
            session.close()
            raise InternalError('database error')

        # If everything is clear, send validation mail to user.
        self._send_activation_code(user.email, user.username, user_activation.activation_code)
        # pipoket: SECURITY ISSUE! PASSWORD SHOULD NOT BE LOGGED!
        #           This logging function will log necessary information but NOT PASSWORD.
        self.logger.info(u"USER REGISTRATION:(username=%s, nickname=%s, email=%s)" %
                (user_reg_info.username, user_reg_info.nickname, user_reg_info.email))
        session.close()
        return activation_code

    def _send_activation_code(self, email, username, activation_code):
        '''
        회원 가입하는 사용자 email로  activation_code를 보내는 함수

        @type  email: string
        @param email: 사용자 E-mail
        @type  username: string
        @param username: 사용자의 User ID
        @type  activation_code: string
        @param activation_code: Confirm Key
        @rtype: none
        @return: None
        '''
        # TODO: exception 적절하게 handling 하기
        # TODO: _charset 이 왜 euc_kr 로 되어있는 걸까?

        title = etc.arara_settings.MAIL_TITLE['activation']
        content = etc.arara_settings.MAIL_CONTENT['activation']
        confirm_url = 'http://' + etc.arara_settings.WARARA_SERVER_ADDRESS + '/account/confirm/%s/%s' % (username.strip(), activation_code)
        confirm_link = '<a href=\'%s\'>%s</a>' % (confirm_url, confirm_url)
        confirm_key = '<br />Confirm Key : %s' % activation_code

        send_mail(title, email, content + confirm_link + confirm_key)

    @require_login
    @log_method_call_important
    def backdoor_confirm(self, session_key, username):
        '''
        인증코드 없이 시샵이 사용자의 등록 할 수 있게 해준다
        예외상황:
            1. 시샵이 아닌 경우: InvalidOperation('not sysop')
            2. 사용자가 없는 경우: InvalidOperation('user does not exist')
            3. 이미 인증이 된 사용자의 경우: InvalidOperation('already confirmed')
            4. 데이터베이스 오류: InternalError('database error')

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  username: string
        @param username: User ID
        '''
        # TODO: check_sysop 같은 함수를 구현하여 만들자.
        # TODO: 사용자 Query 하는 함수 별도로 분리하기
        username = smart_unicode(username)

        if not self.is_sysop(session_key):
            raise InvalidOperation('not sysop')

        session = model.Session()
        user = self._get_user(session, username, 'user does not exist')
        try:
            user_activation = session.query(model.UserActivation).filter_by(user_id=user.id).one()
        except InvalidRequestError:
            if user.activated == True:
                session.close()
                raise InvalidOperation('already confirmed')
            else:
                session.close()
                raise InternalError('database error')

        user_activation.user.activated = True
        session.delete(user_activation)
        session.commit()
        session.close()

    @log_method_call
    def confirm(self, username_to_confirm, activation_code):
        '''
        인증코드(activation code) 확인.
        예외상황:
            1. 잘못된 인증코드 입력시: InvalidOperation('wrong activation code')

        @type  username_to_confirm: string
        @param username_to_confirm: Confirm 하고자 하는 Username
        @type  activation_code: string
        @param activation_code: Confirm Key
        '''
        # TODO: user 쿼리하는 거 별도로 분리하기
        username_to_confirm = smart_unicode(username_to_confirm)

        session = model.Session()
        user = self._get_user(session, username_to_confirm, 'user does not exist')
        try:
            user_activation = session.query(model.UserActivation).filter_by(user_id=user.id).one()
        except InvalidRequestError:
            if user.activated == True:
                session.close()
                raise InvalidOperation('already confirmed')
            else:
                session.close()
                raise InternalError('database error')

        if user_activation.activation_code == activation_code:
            user_activation.user.activated = True
            session.delete(user_activation)
            session.commit()
            session.close()
            return
        else:
            session.close()
            raise InvalidOperation('wrong confirm key')

    def cancel_confirm(self, username):
        '''
        사용자의 이메일 인증을 해제하고 다른 사용자가 해당 이메일을 사용할 수 있도록 함

        @type  username: string
        @param username: 사용자의 User ID
        @rtype: None
        @return: None
        '''

        username_ = smart_unicode(username)

        session = model.Session()
        user = self._get_user(session, username, 'user does not exist')

        if not user.activated:
            raise InvalidOperation('Not confirmed')

        key = (user.username + user.nickname + str(time.time()))
        activation_code = hashlib.md5(key).hexdigest()

        try:
            user_activation = model.UserActivation(user, activation_code)
            session.add(user_activation)

            user.activated = False
            user.email = u''
            session.commit()
        except IntegrityError:
            session.rollback()
            session.close()
            raise InvalidOperation('already canceled')
        except:
            raise InternalError('database error')

    @log_method_call
    def is_registered(self, username):
        '''
        등록된 사용자인지의 여부를 알려준다.
        Confirm은 하지 않았더라도 등록되어있으면 True를 리턴한다.

        @type  username: string
        @param username: Username to check whether is registered or not
        @rtype: bool
        @return: 사용자의 존재유무
        '''
        # TODO: Query 분리하기

        session = model.Session()
        query = session.query(model.User).filter_by(username=username)
        try:
            user = query.one()
            session.close()
            return True
        except InvalidRequestError:
            session.close()
            return False

    @log_method_call
    def is_registered_nickname(self, nickname):
        '''
        등록된 nickname인지의 여부를 알려준다.
        Confirm은 하지 않았더라도 등록되어있으면 True를 리턴한다.

        @type  nickname: string
        @param nickname: Nickname to check whether is registered or not
        @rtype: bool
        @return: Nickname을 사용하는 사용자의 존재유무
        '''
        # TODO: Query 분리하기

        session = model.Session()
        query = session.query(model.User).filter_by(nickname=nickname)
        try:
            user = query.one()
            session.close()
            return True
        except InvalidRequestError:
            session.close()
            return False

    @log_method_call
    def is_registered_email(self, email):
        '''
        등록된 이메일인지의 여부를 알려준다.
        Confirm하지 않았더라도 등록되어있으면 True를 리턴한다.

        @type  email: string
        @param email: E-mail to check whether registered or not.
        @rtype: bool
        @return: Email 주소를 가진 사용자의 존재유무
        '''
        # TODO: Query 분리하기
        session = model.Session()
        query = session.query(model.User).filter_by(email=email)
        try:
            user = query.one()
            session.close()
            return True
        except InvalidRequestError:
            session.close()
            return False

    @require_login
    @log_method_call
    def get_info(self, session_key):
        '''
        회원 정보 수정을 위해 현재 로그인된 회원 자신의 정보를 가져오는 함수.
        다른 사용자의 정보를 열람하는 query와 다름.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: ttypes.UserInformation
        @return:
            1. 가져오기 성공: user_dic
            2. 가져오기 실패:
                1. 로그인되지 않은 유저: InvalidOperation('NOT_LOGGEDIN')
                2. 존재하지 않는 회원: InvalidOperation('MEMBER_NOT_EXIST')
                3. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR')
        '''
        session = model.Session()
        username = self.engine.login_manager.get_session(session_key).username
        username = smart_unicode(username)
        user = self._get_user(session, username, 'member does not exist')
        user_dict = filter_dict(user.__dict__, USER_PUBLIC_WHITELIST)
        if user_dict['last_logout_time']:
            user_dict['last_logout_time'] = datetime2timestamp(
                    user_dict['last_logout_time'])
        else:
            user_dict['last_logout_time'] = 0
        session.close()
        return UserInformation(**user_dict)

    @require_login
    def modify_password(self, session_key, user_password_info):
        '''
        회원의 password를 수정.

        ---user_password_info {username, current_password, new_password}

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  user_password_info: ttypes.UserPasswordInfo
        @param user_password_info: 사용자의 비밀번호 정보
        @rtype: void
        @return:
            1. modify 성공: void
            2. modify 실패:
                1. 수정 권한 없음: 'NO_PERMISSION'
                2. 잘못된 현재 패스워드: 'WRONG_PASSWORD'
                3. 로그인되지 않은 유저: InvalidOperation('NOT_LOGGEDIN')
                4. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR')
        '''
        # TODO: 쿼리 바깥으로 빼기
        # TODO: 비밀번호 암호화하여 전달하기
        session_info = self.engine.login_manager.get_session(session_key)
        username = smart_unicode(session_info.username)
        session = model.Session()
        user = self._get_user(session, username)
        try:
            if not username == user_password_info.username:
                raise NoPermission()
            if not user.compare_password(user_password_info.current_password):
                raise WrongPassword()
            user.set_password(user_password_info.new_password)
            session.commit()
            # pipoket: SECURITY ISSUE! PASSWORD SHOULD NOT BE LOGGED!
            #           This logging function will log necessary information but NOT PASSWORD.
            self.logger.info(u"PASSWORD CHANGE:(username=%s)" % username)
            session.close()
            return

        except NoPermission:
            session.close()
            raise InvalidOperation('no permission')

        except WrongPassword:
            session.close()
            raise InvalidOperation('wrong password')

        except KeyError:
            session.close()
            raise NotLoggedIn()

    @require_login
    def modify_password_sysop(self, session_key, user_password_info):
        '''
        회원의 password를 시삽이 강제로 수정.

        @type  session_key: string
        @param session_key: 사용자 Login Session (SYSOP)
        @type  user_password_info: ttypes.UserPasswordInfo
        @param user_password_info: 사용자의 비밀번호 정보
        @rtype: void
        @return:
            1. modify 성공: void
            2. modify 실패:
                1. 로그인되지 않은 사용자: NotLoggedIn
                2. 사용자가 존재하지 않을 경우: InvalidOperation('user does not exist')
                3. 수정 권한 없음: InvalidOperation('no permission')
                4. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR')
        '''
        # TODO: 쿼리 밖으로 빼기
        # TODO: check_sysop 구현하여 그걸 쓰기
        if not self.is_sysop(session_key):
            raise InvalidOperation('no permission')

        username = smart_unicode(user_password_info.username)
        session = model.Session()
        user = self._get_user(session, username, 'user does not exist')
        user.set_password(user_password_info.new_password)
        session.commit()
        self.logger.info(u"PASSWORD CHANGE:(username=%s)" % username)
        session.close()

    def modify_password_with_token(self, user_password_info, token_code):
        '''
        Recovery Token을 사용하여 비밀번호를 수정

        ---user_password_info {username, current_password, new_password}

        @type  user_password_info: ttypes.UserPasswordInfo
        @param user_password_info: 사용자의 비밀번호 정보
        @rtype: void
        @return:
            1. modify 성공: void
            2. modify 실패:
                1. 잘못된 토큰: InvalidOperation('INVALID_APPROACH')
                2. DB 에러 : InternalError
        '''
        # TODO: 비밀번호 암호화하여 전달하기
        session = model.Session()
        user = self._get_user(session, user_password_info.username)
        try:
            token = session.query(model.LostPasswordToken).filter_by(user_id=user.id, code=token_code).one()
        except NoResultFound:
            session.close()
            raise InvalidOperation('INVALID_APPROACH')
        except MultipleResultsFound:
            session.close()
            raise InternalError()

        user.set_password(user_password_info.new_password)
        session.delete(token)
        session.commit()
        # pipoket: SECURITY ISSUE! PASSWORD SHOULD NOT BE LOGGED!
        #           This logging function will log necessary information but NOT PASSWORD.
        self.logger.info(u"PASSWORD CHANGE:(username=%s)" % user_password_info.username)
        session.close()

    @require_login
    @log_method_call_important
    def modify_user(self, session_key, user_modification):
        '''
        password를 제외한 회원 정보 수정

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  user_reg_infot: ttypes.UserModification
        @param user_reg_infot: 변경할 사용자 정보
        @rtype: void
        @return:
            1. modify 성공: void
            2. modify 실패:
                1. 로그인되지 않은 유저: InvalidOperation('NOT_LOGGEDIN'
                2. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR'
                3. 양식이 맞지 않음(부적절한 NULL값 등): 'WRONG_DICTIONARY'
        '''
        session_info = self.engine.login_manager.get_session(session_key)
        username = smart_unicode(session_info.username)

        if not is_keys_in_dict(user_modification.__dict__,
                               USER_PUBLIC_MODIFIABLE_WHITELIST):
            raise InvalidOperation('wrong input')
        session = model.Session()
        user = self._get_user(session, username)

        for key, value in user_modification.__dict__.items():
            # 문자열에 한하여 smart_unicode 로 변환하여 저장한다
            if type(value) in [str, unicode]:
                setattr(user, key, smart_unicode(value))
            else:
                setattr(user, key, value)
        session.commit()
        session.close()

        # Member Manager Cache
        ara_memcached.clear_memcached(self.get_listing_mode, session_info.id)

    # @require_login
    @log_method_call_important
    def modify_authentication_email(self, username, new_email):
        '''
        인증되지 않은 이메일 주소의 변경

        @type  username: string
        @param username: Username
        @type  new_email: string
        @param new_email: New E-mail Address for Authentication
        @rtype: void
        @return:
            1. modify 성공: void
            2. modify 실패:
                1. 로그인되지 않은 유저: InvalidOperation('not logged in')
                2. 유저를 찾을 수 없음: InvalidOperation('user not found')
                3. 올바르지 않은 이메일 주소: InvalidOperation('wrong email address')
                3. 데이터베이스 오류: InternalError('database error')
        '''
        # TODO: 사용자 쿼리 밖으로 빼기
        session = model.Session()
        username = smart_unicode(username)
        if new_email:
            if not PROPER_EMAIL_REGEX.match(new_email):
                raise InvalidOperation('email other than @KAIST not permitted')
            user_with_email = session.query(model.User).filter_by(email=new_email).all()
            if user_with_email:
                user_with_email = user_with_email[0]
                if user_with_email.username != username: # To allow send email to him/her again
                    raise InvalidOperation(u'Other user(username:%s) already uses %s!' % (user_with_email.username, new_email))
            try:
                user = self._get_user(session, username, 'wrong username')
                try:
                    user_activation = session.query(model.UserActivation).filter_by(user=user).one()
                except NoResultFound: # TODO: Test is needed
                    key = user.username + user.password + user.nickname
                    activation_code = hashlib.md5(key).hexdigest()
                    # Register activate code to db
                    user_activation = model.UserActivation(user, activation_code)
                    session.add(user_activation)
                    session.commit()

                user_activation = session.query(model.UserActivation).filter_by(user=user).one()
                activation_code = user_activation.activation_code
                if user.email != new_email:
                    user.email = new_email
                    session.commit()
                self._send_activation_code(user.email, user.username, activation_code)
                session.close()
            except Exception:
                import traceback
                logging.warn(traceback.format_exc())
                session.close()
                raise InternalError('database error')
        else:
            raise InvalidOperation('wrong email address')


    @require_login
    @log_method_call
    def query_by_username(self, session_key, username):
        '''
        username 기반 쿼리 함수. 다른 사용자의 정보를 알아내는 데 사용한다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  username: string
        @param username: User ID to send Query
        @rtype: ttypes.PublicUserInformation
        @return:
            1. 쿼리 성공: query_dic
            2. 쿼리 실패:
                1. 존재하지 않는 아이디: InvalidOperation('QUERY_ID_NOT_EXIST')
                2. 로그인되지 않은 유저: InvalidOperation('NOT_LOGGEDIN')
                3. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR')
        '''
        # TODO: Exception 내용 정정
        username = smart_unicode(username)
        session = model.Session()
        query_user = self._get_user(session, username, 'Query username does not exist')
        query_user_dict = filter_dict(query_user.__dict__, USER_QUERY_WHITELIST)
        if query_user_dict['last_logout_time']:
            query_user_dict['last_logout_time'] = datetime2timestamp(
                    query_user_dict['last_logout_time'])
        else:
            query_user_dict['last_logout_time'] = 0
        session.close()
        return PublicUserInformation(**query_user_dict)

    @require_login
    @log_method_call
    def query_by_nick(self, session_key, nickname):
        '''
        nickname 기반 쿼리 함수. 다른 사용자의 정보를 알아내는 데 사용한다.


        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  username: string
        @param nickname: User Nickname to send Query
        @rtype: ttypes.PublicUserInformation
        @return:
            1. 쿼리 성공: query_dic
            2. 쿼리 실패:
                1. 존재하지 않는 닉네임: InvalidOperation('QUERY_NICK_NOT_EXIST'
                2. 로그인되지 않은 유저: InvalidOperation('NOT_LOGGEDIN'
                3. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR'
        '''
        # TODO: 쿼리 밖으로 빼기
        nickname = smart_unicode(nickname)
        session = model.Session()
        try:
            query_user = session.query(model.User).filter_by(
                    nickname=nickname).filter_by(deleted=False).one()
            query_user_dict = filter_dict(query_user.__dict__,
                                          USER_QUERY_WHITELIST)
            if query_user_dict['last_logout_time']:
                query_user_dict['last_logout_time'] = datetime2timestamp(
                        query_user_dict['last_logout_time'])
            else:
                query_user_dict['last_logout_time'] = 0
            session.close()
            return PublicUserInformation(**query_user_dict)
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('query nickname does not exist')


    @require_login
    @log_method_call_important
    def remove_user(self, session_key):
        '''
        session key로 로그인된 사용자를 등록된 사용자에서 제거하고, Primary Key Violation 방지와 재가입 꼼수 방지를 위해 적절한 placeholder를 같은 primary key와 같은 ID, email로서 배치한다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: void
        @return:
            1. 성공시: void
            2. 실패시: NotLoggedIn
        '''
        session = model.Session()
        username = smart_unicode(self.engine.login_manager.get_session(session_key).username)

        try:
            user = session.query(model.User).filter_by(username=username).one()

            # Create placeholder
            user.password = u'youcannotlogin'
            user.nickname = u'탈퇴회원'
            user.signature = u''
            user.self_introduction = u''
            user.deleted = True

            # Clean-Up almost everythings
            session.query(model.UserActivation).filter_by(user_id=user.id).delete()
            session.query(model.BBSManager).filter_by(manager_id=user.id).delete()
            session.query(model.ScrapStatus).filter_by(user_id=user.id).delete()
            session.query(model.Blacklist).filter(or_(model.Blacklist.user_id==user.id, model.Blacklist.blacklisted_user_id==user.id)).delete()
            session.query(model.SelectedBoards).filter_by(user_id=user.id).delete()
            session.query(model.LostPasswordToken).filter_by(user_id=user.id).delete()

            session.commit()
            session.close()

            return

        except KeyError:
            session.close()
            raise NotLoggedIn()

    @log_method_call
    def search_user(self, session_key, search_user, search_key=None):
        '''
        찾고자 하는 username와 nickname에 해당하는 user를 찾아주는 함수
        search_key 가 username 또는 nickname 으로 주어질 경우 해당하는 search key로만 찾는다
        (주어지지 않으면 두 방향 모두에 대하여 찾는다)

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  search_user: string
        @param search_user: User Info(username or nickname)
        @type  search_key: string
        @param search_key: Search key
        @rtype: list<ttypes.SearchUserResult>
        @return:
            1. 성공시: True, {'username':'kmb1109','nickname':'mikkang'}
            2. 실패시:
                1. 존재하지 않는 사용자: InvalidOperation('NOT_EXIST_USER'
                2. 잘못된 검색 키:InvalidOperation('INCORRECT_SEARCH_KEY')
        '''
        # TODO: session_key 를 이용한 Login check
        # TODO: 쿼리 직접 쓰지 말고 나머지 두 함수 합쳐서 할 것
        # TODO: SearchUserResult 는 뭐고 PublicUserInformation 는 뭔가?
        search_user = smart_unicode(search_user)

        session = model.Session()
        try:
            if not search_key:
                user = session.query(model.User).filter(
                        or_(model.User.username==search_user,
                            model.User.nickname==search_user)).filter_by(deleted=False).all()
            else:
                if search_key.lower() == u'username':
                    user = session.query(model.User).filter_by(
                            username=search_user).filter_by(deleted=False).all()
                elif search_key.lower() == u'nickname':
                    user = session.query(model.User).filter_by(
                            nickname=search_user).filter_by(deleted=False).all()
                else:
                    session.close()
                    raise InvalidOperation('incorrect search key')
            user_dict_list = self._get_dict_list(user, USER_SEARCH_WHITELIST)
            user_list = [SearchUserResult(**x) for x in user_dict_list]
            session.close()
            return user_list
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('user does not exist')
        except AssertionError:
            session.close()
            raise InvalidOperation('invalid key')

    @log_method_call
    def send_id_recovery_email(self, email):
        '''
        ID를 잃어버렸을 때, e-mail 기반으로 id를 찾아서 그 이메일로 id를 전송해주는 함수.
        성공할 경우 True, 실패할 경우 False를 반환한다.

        @type  email: string
        @param email: 이메일 주소
        @rtype: bool
        @return:
            1. 성공 시 : True
            2. 실패 시 : False
        '''
        session = model.Session()
        query = session.query(model.User).filter_by(email=email)
        try:
            user = query.one()
            session.close()
        except NoResultFound:
            session.close()
            return False

        title = arara_settings.MAIL_TITLE['id_recovery']
        content = arara_settings.MAIL_CONTENT['id_recovery']
        content += ' Here is your ARA account username which is associated with %s <br /><br /> ' % email
        content += '    Your ID  :  %s   <br /><br />' % user.username
        content += ' Please visit http://' + arara_settings.WARARA_SERVER_ADDRESS + '<br /><br />'
        content += ' This is post-only mailing. <br /> Thanks. '
        send_mail(title, email, content)

        return True

    @log_method_call
    def send_password_recovery_email(self, username, email):
        '''
        비밀번호를 분실했을 때, username과 등록된 email 주소가 맞으면 패스워드를 변경할 수 있는 일회용 Token을 생성해 이메일로 전송한다.

        @type  username: string
        @param username: 비밀번호를 찾으려는 유저 이름
        @type  email: string
        @param email: 등록된 E-mail 주소
        @rtype: None
        @return: None
        '''
        session = model.Session()
        user = self._get_user(session, username)

        if user.email != email:
            raise InvalidOperation("No account found with that email address.")

        session.query(model.LostPasswordToken).filter_by(user_id=user.id).delete()
        session.flush()

        generated_string = ''.join([random.choice(string.lowercase + string.uppercase + string.digits) for i in range(24)])
        token = model.LostPasswordToken(user_id=user.id, code=generated_string)
        session.add(token)
        session.commit()
        session.close()

        url = 'http://' + etc.arara_settings.WARARA_SERVER_ADDRESS + '/account/recover/%s/%s/' % (username, generated_string)
        title = arara_settings.MAIL_TITLE['password_recovery']
        content = arara_settings.MAIL_CONTENT['password_recovery'] + '<a href=\'%s\'>%s</a>' % (url, url)
        send_mail(title, email, content)

    @require_login
    @log_method_call_important
    def is_sysop(self, session_key):
        '''
        로그인한 user가 SYSOP인지 아닌지를 확인하는 함수

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: bool
        @return:
            1. SYSOP일시: True
            2. SYSOP이 아닐시: False
            3. 예외 발생시:
                1. 로그인되지 않은 사용자: NotLoggedIn
                2. 사용자가 존재하지 않을 경우: InvalidOperation('user does not exist')
        '''
        session = model.Session()
        user_info = self.engine.login_manager.get_session(session_key)
        user = self._get_user(session, user_info.username, 'user does not exist')
        session.close()
        return user.is_sysop


    def user_to_sysop(self, session_key, username):
        '''
        user를 SYSOP으로 바꿔주는 함수

        @type  session_key: string
        @param session_key: 사용자 Login Session (must be SYSOP)
        @type username_string
        @param username: Username that will be SYSOP
        @return:
            1. 성공했을 경우: void
            2. 실패했을 경우: Invalid Operation
        '''
        # TODO: 사용자 쿼리 밖으로 빼기
        # TODO: sysop 인지 체크하는 거 밖으로 빼기

        if not self.is_sysop(session_key):
            raise InvalidOperation('no permission')

        username = smart_unicode(username)
        session = model.Session()

        user = self._get_user(session, username, 'user does not exist')
        if user.is_sysop:
            session.close()
            raise InvalidOperation('already sysop..')
        user.is_sysop = True
        session.commit()
        session.close()

    def authentication_mode(self, session_key):
        '''
        로그인한 user의 인증단계를 확인하는 함수

        @type session_key: string
        @param session_key: 사용자 Login Session
        @rtype: int
        @return:
            1. 비회원 : 0
            2. 메일인증(non @kaist) : 1
            3. 메일인증(@kaist) : 2
            4. 포탈인증 : 3
        '''
        session = model.Session()
        user = self._get_user_by_session(session, session_key)
        return user.authentication_mode

    def change_listing_mode(self, session_key, listing_mode):
        '''
        로그인한 user의 listing mode (글 목록 정렬 방식) 를 변경한다.

        @type  session_key: string
        @param session_key: 사용자 Login Session (must be SYSOP)
        @type  listing_mode: int
        @param listing_mode: 글 목록 정렬 방식 (ArticleManager 참고)
        @return:
            1. 성공했을 경우: void
            2. 실패했을 경우 : Invalid Operation
        '''
        if listing_mode < 0 or 1 < listing_mode:
            raise InvalidOperation('wrong listing mode')

        session = model.Session()
        user = self._get_user_by_session(session, session_key)
        user_id = user.id
        try:
            user.listing_mode = listing_mode
            session.commit()
            session.close()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('database error')

        # Cache update
        ara_memcached.clear_memcached(self.get_listing_mode, user_id)

    @ara_memcached.memcached_decorator
    def get_listing_mode(self, user_id):
        '''
        사용자의 listing_mode (글 목록 정렬 방식) 을 돌려준다.
        user_id 를 직접 사용하므로 내부 사용 전용.

        @type  user_id: int
        @param user_id: 사용자 고유 id
        @rtype: int
        @return: 해당 사용자의 글 목록 정렬 방식
        '''
        # 존재하지 않는 사용자에 대한 기본값 처리
        if user_id == -1:
            return 0

        session = model.Session()
        try:
            user = self._get_user_by_id(session, user_id)
            result = user.listing_mode
            session.close()
            return result
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('uesr does not exist')

    def get_listing_mode_by_key(self, session_key):
        '''
        로그인한 사용자의 listing_mode (글 목록 정렬 방식) 을 돌려준다.
        만일 로그인하지 않은 사용자라면 그냥 0 (default) 을 돌려준다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: int
        @return: 해당 사용자의 글 목록 정렬 방식
        '''
        # 로그인되지 않은 사용자에 대한 기본값 처리
        if session_key == '':
            return 0

        return self.get_listing_mode(self.engine.login_manager.get_user_id(session_key))

    def get_activated_users(self, session_key, limit = -1):
        '''
        전체 사용자들 중 사용자 인증이 된 사용자들의 목록을 돌려준다.
        SYSOP 만 사용 가능.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  limit: int
        @param limit: 최대 몇 명의 사용자를 돌려줄 것인가. -1 일 때는 모든 사용자
        @rtype: list<arara_thrift.SearchUserResult>
        @return: 사용자 인증이 된 사용자들의 목록
        '''
        if not self.is_sysop(session_key):
            raise InvalidOperation('not sysop')

        session = model.Session()
        query = session.query(model.User).filter_by(activated=True)
        users = query.all()
        # 갯수 제한 설정
        if limit > len(users):
            limit = len(users)

        result = [None] * limit

        for idx, user in enumerate(users):
            if limit == idx: # limit == -1 이면 절대 여기 걸리지 않는다
                break        # 한편 그 외의 경우엔 limit 갯수만큼만 통과
            result[idx] = SearchUserResult(**self._get_dict(user, USER_SEARCH_WHITELIST))

        session.close()

        return result

    @ara_memcached.memcached_decorator
    def get_selected_boards(self, session_key):
        '''
        사용자들이 선택한 몇 개의 즐겨찾는 게시판 목록을 반환하는 함수이다.

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @rtype: list<ttypes.Board>
        @return: 주어진 사용자가 즐겨찾기 한 게시판들의 목록
        '''
        session = model.Session()
        user = self._get_user_by_session(session, session_key)
        boards = user.selected_boards
        ttypes_boards = [self.engine.board_manager.get_board(x.board.board_name) for x in boards]
        session.close()

        return ttypes_boards

    def set_selected_boards(self, session_key, board_ids):
        '''
        boards_id로 주어진 게시판들을 주어진 사용자의 즐겨찾는 게시판으로 설정한다

        @type  session_key: string
        @param session_key: 사용자 Login Session
        @type  board_ids: list<int>
        @param board_ids: 게시판들의 아이디 목록
        @rtype: void
        @return: None
        '''
        session = model.Session()
        user = self._get_user_by_session(session, session_key)

        if len(board_ids) >3:
            session.close()
            raise InvalidOperation("Please check 3 boards at most")
        try:
            boards = [session.query(model.Board).filter_by(id=x).one() for x in board_ids]
        except NoResultFound, MultipleResultsFound:
            session.close()
            raise InvalidOperation("Not a valid board id")

        session.query(model.SelectedBoards).filter_by(user_id=user.id).delete()
        session.flush()

        for board in boards:
            selected_board = model.SelectedBoards(user, board)
            session.add(selected_board)
        session.commit()
        session.close()

        # Cache update
        ara_memcached.clear_memcached(self.get_selected_boards, session_key)

    __public__ = [
            authenticate,
            register_,
            backdoor_confirm,
            confirm,
            cancel_confirm,
            is_registered,
            is_registered_nickname,
            is_registered_email,
            get_info,
            modify_password,
            modify_password_sysop,
            modify_password_with_token,
            modify_user,
            modify_authentication_email,
            query_by_username,
            query_by_nick,
            remove_user,
            search_user,
            send_id_recovery_email,
            send_password_recovery_email,
            is_sysop,
            logout_process,
            get_activated_users,
            set_selected_boards,
            get_selected_boards,
            update_last_logout_time,
            get_listing_mode,
            get_listing_mode_by_key]
