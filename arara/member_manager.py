# -*- coding: utf-8 -*-

import md5
import datetime
import time
import logging
import smtplib
from email.MIMEText import MIMEText

from sqlalchemy.exceptions import InvalidRequestError, IntegrityError
from sqlalchemy import or_, not_, and_

from arara_thrift.ttypes import *
from arara import model
from arara.util import require_login, filter_dict, is_keys_in_dict
from arara.util import log_method_call_with_source, log_method_call_with_source_important
from arara.util import smart_unicode, datetime2timestamp

log_method_call = log_method_call_with_source('member_manager')
log_method_call_important = log_method_call_with_source_important('member_manager')

class NoPermission(Exception):
    pass

class WrongPassword(Exception):
    pass

class NotLoggedIn(Exception):
    pass

USER_PUBLIC_KEYS = ['username', 'password', 'nickname', 'email',
        'signature', 'self_introduction', 'default_language']
USER_QUERY_WHITELIST = ('username', 'nickname', 'email',
        'signature', 'self_introduction', 'last_login_ip', 'last_logout_time')
USER_PUBLIC_WHITELIST= ('username', 'nickname', 'email', 'last_login_ip',
        'last_logout_time', 'signature', 'self_introduction',
        'default_language', 'activated', 'widget', 'layout')
USER_PUBLIC_MODIFIABLE_WHITELIST= ('nickname', 'signature',
        'self_introduction', 'default_language', 'widget', 'layout')
USER_SEARCH_WHITELIST = ('username', 'nickname')

class MemberManager(object):
    '''
    회원 가입, 회원정보 수정, 회원정보 조회, 이메일 인증등을 담당하는 클래스
    '''

    def __init__(self):
        # mock data
        self.member_dic = {}  # DB에서 member table를 read해오는 부분
        # 초기 시샵 생성
        #if not self.is_registered('SYSOP'):
        self._register_sysop()

    def _register_sysop(self):
        sysop_reg_dic = {'username':u'SYSOP', 'password':u'SYSOP',
                'nickname':u'SYSOP', 'email':u'SYSOP@sparcs.org',
                'signature':u'', 'self_introduction':u'i am mikkang',
                'default_language':u'ko_KR'}
        try:
            user = model.User(**sysop_reg_dic)
            session = model.Session()
            session.save(user)
            user.activated = True
            user.is_sysop = True
            session.commit()
        except IntegrityError:
            session.rollback()
            pass

    def _set_login_manager(self, login_manager):
        self.login_manager = login_manager

    @log_method_call
    def _logout_process(self, username):
        session = model.Session()
        try:
            user = session.query(model.User).filter_by(username=username).one()
            user.last_logout_time = datetime2timestamp(datetime.datetime.fromtimestamp(time.time()))
            session.commit()
            session.close()
            return
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('DATABASE_ERROR')

    @log_method_call
    def authenticate(self, username, password, user_ip):
        session = model.Session()
        try:
            user = session.query(model.User).filter_by(username=username).one()
            if user.compare_password(password) and user.activated == True:
                user.last_login_time = datetime.datetime.fromtimestamp(time.time())
                user.last_login_ip = unicode(user_ip)
                ret = {'last_login_time': datetime2timestamp(
                    user.last_login_time),
                       'nickname': user.nickname}
                session.commit()
                session.close()
                return AuthenticationInfo(**ret)
            else:
                session.close()
                if user.activated:
                    raise InvalidOperation('WRONG_PASSWORD')
                else:
                    raise InvalidOperation('NOT_ACTIVATED')
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('WRONG_USERNAME')
   
    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
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

    @log_method_call
    def register(self, user_reg_info):
        '''
        DB에 회원 정보 추가. activation code를 발급한다.
        예외상황:
            1. 시샵이 아이디인 경우: InvalidOperation('permission denied')
            2. 이미 가입한 사용자의 경우: InvalidOperation('already added')
            3. 데이터베이스 오류: InternalError('database error')

        @type  user_reg_info: arara_thrift.UserRegistration
        @param user_reg_info: 사용자의 회원가입 정보를 담은 객체
        @rtype: string
        @return: 사용자 인증코드
        '''

        if user_reg_info.username.lower() == 'sysop':
            raise InvalidOperation('permission denied')

        key = (user_reg_info.username +
            user_reg_info.password + user_reg_info.nickname)
        activation_code = md5.md5(key).hexdigest()
        
        session = model.Session()
        try:
            # Register user to db
            user = model.User(**user_reg_info.__dict__)
            session.save(user)
            # Register activate code to db
            user_activation = model.UserActivation(user, activation_code)
            session.save(user_activation)
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
        # Frontend should send the email I guess, so quoted the line below 090105
        # Re-uncommented by combacsa, 090112. Frontend never send the email.
        self._send_mail(user.email, user.username, user_activation.activation_code)
        session.close()
        return activation_code

    
    def _send_mail(self, email, username, activation_code):
        '''
        회원 가입하는 사용자 email로  activation_code를 보내는 함수 

        @type  email: string
        @param email: 사용자 E-mail
        @type  username: string
        @param username: User ID
        @type  activation_code: string
        @param activation_code: Confirm Key
        @rtype: string
        @return: None
        '''
        SERVER_ADDRESS = 'arara.kaist.ac.kr'

        try:
            HOST = 'localhost'
            sender = 'root_id@sparcs.org'
            content = 'You have been successfully registered as the ARAra member.<br />To use your account, you have to activate it.<br />Please click the link below on any web browser to activate your account.<br /><br />'
            confirm_url = 'http://' + SERVER_ADDRESS + '/account/confirm/%s/%s' % (username, activation_code)
            confirm_link = '<a href=\'%s\'>%s</a>' % (confirm_url, confirm_url)
            title = "[ARAra] Please activate your account"
            msg = MIMEText(content+confirm_link, _subtype="html", _charset='euc_kr')
            msg['Subject'] = title
            msg['From'] = sender
            msg['To'] = email
            s = smtplib.SMTP()
            s.connect(HOST)
            s.sendmail(sender, [email], msg.as_string())
            s.quit()
        except Exception:
            raise


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
        @param session_key: User Key
        @type  username: string
        @param username: User ID
        '''
        username = smart_unicode(username)
        
        if not self.is_sysop(session_key):
            raise InvalidOperation('not sysop')

        session = model.Session()
        try:
            user = session.query(model.User).filter(model.User.username == username).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('user does not exist')
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
        @param username_to_confirm: Confirm Username
        @type  activation_code: string
        @param activation_code: Confirm Key
        '''
        username_to_confirm = smart_unicode(username_to_confirm)
        
        session = model.Session()
        try:
            user = session.query(model.User).filter(model.User.username == username_to_confirm).one()
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('user does not exist')
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
        

    @log_method_call
    def is_registered(self, username):
        '''
        등록된 사용자인지의 여부를 알려준다.
        Confirm은 하지 않았더라도 등록되어있으면 True를 리턴한다.

        >>> member_manager.is_registered('mikkang')
        True

        @type  username: string
        @param username: Username to check whether is registered or not
        @rtype: bool
        @return: 사용자의 존재유무
        '''
        #remove quote when MD5 hash for UI is available
        #

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

        >>> member_manager.is_registered_nickname('mikkang')
        True

        @type  nickname: string
        @param nickname: Nickname to check whether is registered or not
        @rtype: bool
        @return: Nickname을 사용하는 사용자의 존재유무
        '''
        #remove quote when MD5 hash for UI is available
        #

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

        >>> member_manager.is_registered_email('pipoket@hotmail.com')
        False

        @type  email: string
        @param email: E-mail to check whether registered or not.
        @rtype: bool
        @return: Email 주소를 가진 사용자의 존재유무
        '''
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
        회원 정보 수정을 위해 현재 로그인된 회원의 정보를 가져오는 함수.
        다른 사용자의 정보를 열람하는 query와 다름.

        @type  session_key: string
        @param session_key: User Key
        @rtype: dictionary
        @return:
            1. 가져오기 성공: True, user_dic
            2. 가져오기 실패:
                1. 로그인되지 않은 유저: InvalidOperation('NOT_LOGGEDIN'
                2. 존재하지 않는 회원: InvalidOperation('MEMBER_NOT_EXIST'
                3. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR'
        '''
        try:
            session = model.Session()
            username = self.login_manager.get_session(session_key).username
            user = session.query(model.User).filter_by(username=username).one()
            user_dict = filter_dict(user.__dict__, USER_PUBLIC_WHITELIST)
            if not user_dict['last_logout_time']:
                user_dict['last_logout_time'] = 0
            session.close()
            return UserInformation(**user_dict)
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('member does not exist')

    @require_login    
    @log_method_call_important
    def modify_password(self, session_key, user_password_info):
        '''
        회원의 password를 수정.

        ---user_password_info {username, current_password, new_password}

        @type  session_key: string
        @param session_key: User Key
        @type  user_password_info: Dictionary
        @param user_password_info: User Dictionary
        @rtype: string
        @return:
            1. modify 성공: True, 'OK'
            2. modify 실패:
                1. 수정 권한 없음: 'NO_PERMISSION'
                2. 잘못된 현재 패스워드: 'WRONG_PASSWORD'
                3. 로그인되지 않은 유저: InvalidOperation('NOT_LOGGEDIN'
                4. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR'
        '''
        session_info = self.login_manager.get_session(session_key)
        username = session_info.username
        session = model.Session()
        user = session.query(model.User).filter_by(username=username).one()
        try:
            if not username == user_password_info.username:
                raise NoPermission()
            if not user.compare_password(user_password_info.current_password):
                raise WrongPassword()
            user.set_password(user_password_info.new_password)
            session.commit()
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
    @log_method_call_important
    def modify(self, session_key, user_modification):
        '''
        password를 제외한 회원 정보 수정

        @type  session_key: string
        @param session_key: User Key
        @type  user_reg_infot: dictionary
        @param user_reg_infot: User Dictionary
        @rtype: string
        @return:
            1. modify 성공: True, 'OK'
            2. modify 실패:
                1. 로그인되지 않은 유저: InvalidOperation('NOT_LOGGEDIN'
                2. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR'
                3. 양식이 맞지 않음(부적절한 NULL값 등): 'WRONG_DICTIONARY'
        '''
        session_info = self.login_manager.get_session(session_key)
        username = session_info.username

        if not is_keys_in_dict(user_modification.__dict__,
                               USER_PUBLIC_MODIFIABLE_WHITELIST):
            raise InvalidOperation('wrong input')
        session = model.Session()
        user = session.query(model.User).filter_by(username=username).one()
        for key, value in user_modification.__dict__.items():
            setattr(user, key, value)
        session.commit()
        session.close()
        return

    @require_login
    @log_method_call
    def query_by_username(self, session_key, username):
        '''
        쿼리 함수
        
        ---query_dic { username, nickname, signature, self_introduction, last_login_ip }

        @type  session_key: string
        @param session_key: User Key
        @type  username: string
        @param username: User ID to send Query
        @rtype: dictionary
        @return:
            1. 쿼리 성공: True, query_dic
            2. 쿼리 실패:
                1. 존재하지 않는 아이디: InvalidOperation('QUERY_ID_NOT_EXIST'
                2. 로그인되지 않은 유저: InvalidOperation('NOT_LOGGEDIN'
                3. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR'
        '''
        username = smart_unicode(username)
        try:
            session = model.Session()
            query_user = session.query(model.User).filter_by(username=query_username).one()
            query_user_dict = filter_dict(query_user.__dict__, USER_QUERY_WHITELIST)
            if not query_user_dict['last_logout_time']:
                query_user_dict['last_logout_time'] = 0
            session.close()
            return PublicUserInformation(**query_user_dict)
        except InvalidRequestError:
            session.close()
            raise InvalidOperation('query id does not exist')

    @require_login
    @log_method_call
    def query_by_nick(self, session_key, nickname):
        '''
        쿼리 함수
        
        ---query_dic { username, nickname, signature, self_introduction, last_login_ip }

        @type  session_key: string
        @param session_key: User Key
        @type  nickname: string
        @param nickname: User Nickname to send Query
        @rtype: dictionary
        @return:
            1. 쿼리 성공: True, query_dic
            2. 쿼리 실패:
                1. 존재하지 않는 닉네임: InvalidOperation('QUERY_NICK_NOT_EXIST'
                2. 로그인되지 않은 유저: InvalidOperation('NOT_LOGGEDIN'
                3. 데이터베이스 오류: InvalidOperation('DATABASE_ERROR'
        '''
        nickname = smart_unicode(nickname)
        try:
            session = model.Session()
            query_user = session.query(model.User).filter_by(
                    nickname=query_nickname).one()
            query_user_dict = filter_dict(query_user.__dict__,
                                          USER_QUERY_WHITELIST)
            if not query_user_dict['last_logout_time']:
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
        session key로 로그인된 사용자를 등록된 사용자에서 제거한다' - 회원탈퇴

        @type  session_key: string
        @param session_key: User Key
        @rtype: String
        @return:
            1. 성공시: True, 'OK'
            2. 실패시: InvalidOperation('NOT_LOGGEDIN'
        '''

        session = model.Session()
        username = self.login_manager.get_session(session_key).username
        try:
            user = session.query(model.User).filter_by(username=username).one()
            user.activated = False
            session.commit()
            session.close()
            return
        except KeyError:
            session.close()
            raise NotLoggedIn()
        
    @require_login
    @log_method_call
    def search_user(self, session_key, search_user, search_key=None):
        '''
        member_dic 에서 찾고자 하는 username와 nickname에 해당하는 user를 찾아주는 함수
        search_key 가 username 또는 nickname 으로 주어질 경우 해당하는 search key로만 찾는다

        @type  session_key: string
        @param session_key: User Key
        @type  search_user_info: string
        @param search_user_info: User Info(username or nickname)
        @type  search_key: string
        @param search_key: Search key
        @rtype: dictionary 
        @return:
            1. 성공시: True, {'username':'kmb1109','nickname':'mikkang'} 
            2. 실패시: 
                1. 존재하지 않는 사용자: InvalidOperation('NOT_EXIST_USER'
                2. 잘못된 검색 키:InvalidOperation('INCORRECT_SEARCH_KEY'
        '''
        search_user = smart_unicode(search_user)

        try:
            session = model.Session()
            if not search_key:
                user = session.query(model.User).filter(
                        or_(model.users_table.c.username==search_user,
                            model.users_table.c.nickname==search_user)).all()
            else:
                if search_key.lower() == u'username':
                    user = session.query(model.User).filter_by(
                            username=search_user).all()
                elif search_key.lower() == u'nickname':
                    user = session.query(model.User).filter_by(
                            nickname=search_user).all()
                else:
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

    @require_login
    @log_method_call_important
    def is_sysop(self, session_key):
        '''
        로그인한 user가 SYSOP인지 아닌지를 확인하는 함수
        
        @type  session_key: string
        @param session_key: User Key
        @rtype: bool
        @return:
            1. SYSOP일시: True
            2. SYSOP이 아닐시: False
        '''

        if self.login_manager.get_session(session_key).username == 'SYSOP':
            return True
        else:
            return False

# vim: set et ts=8 sw=4 sts=4
