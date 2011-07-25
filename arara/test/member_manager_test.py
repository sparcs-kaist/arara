#-*- coding: utf-8 -*-
import unittest
import os
import sys

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gen-py/'))
sys.path.append(THRIFT_PATH)
ARARA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(ARARA_PATH)

from arara.test.test_common import AraraTestBase
from arara_thrift.ttypes import *
import arara.model


class MemberManagerTest(AraraTestBase):
    def setUp(self):
        # Common preparation for all tests
        super(MemberManagerTest, self).setUp()

    def _get_user_reg_dic(self, username, manual_setting = {}):
        user_reg_dic = {'username': username, 'password': username, 'nickname': username, 'email': username + '@kaist.ac.kr', 'signature': username, 'self_introduction': username, 'default_language': u'english', 'campus': u'Daejeon'}
        for key in manual_setting:
            if key in user_reg_dic:
                user_reg_dic[key] = manual_setting[key]
        return user_reg_dic

    def _register_user(self, username, manual_setting = {}):
        user_reg_dic = self._get_user_reg_dic(username, manual_setting)
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        return register_key

    def _register_and_confirm(self, username, manual_setting = {}):
        registration_key = self._register_user(username, manual_setting)
        self.engine.member_manager.confirm(username, registration_key)

    def test__register_without_confirm(self):
        '''
        이메일 인증 과정 없이 사용자 등록이 잘 되는지 검사
        사용자를 생성하고, 에러 없이 login 이 되는지로 검증한다
        '''
        # Case 1. SYSOP 권한은 없는 hodduc
        user_reg_dic_hodduc = self._get_user_reg_dic(u'hodduc')
        self.engine.member_manager._register_without_confirm(user_reg_dic_hodduc, False)
        self.engine.login_manager.login(u'hodduc', u'hodduc', u'143.248.234.140')

        # Case 2. SYSOP 권한을 지닌 sillo

        user_reg_dic_sillo = self._get_user_reg_dic(u'sillo')
        self.engine.member_manager._register_without_confirm(user_reg_dic_sillo, True)
        session_key = self.engine.login_manager.login(u'sillo', u'sillo', u'143.248.234.140')
        # 시삽 권한을 가지는지 확인
        if not self.engine.member_manager.is_sysop(session_key):
            self.fail('_register_without_confirm() failed! :: Failed to grant SYSOP previlege')

    def test_is_registered_false(self):
        # 아직 등록한 적이 없는 사용자 정보에 대해 False 여야 한다
        self.assertEqual(False, self.engine.member_manager.is_registered(u'mikkang'))
        self.assertEqual(False, self.engine.member_manager.is_registered_nickname(u'mikkang'))
        self.assertEqual(False, self.engine.member_manager.is_registered_email(u'mikkang@kaist.ac.kr'))

    def test_is_registered_true(self):
        # 이미 등록된 사용자 정보에 대해 True 여야 한다

        # mikkang 사용자를 등록한다
        self._register_and_confirm(u'mikkang')

        self.assertEqual(True, self.engine.member_manager.is_registered(u'mikkang'))
        self.assertEqual(True, self.engine.member_manager.is_registered_nickname(u'mikkang'))
        self.assertEqual(True, self.engine.member_manager.is_registered_email(u'mikkang@kaist.ac.kr'))

    def test_register_(self):
        # mikkang 사용자를 등록한다.
        # 이 과정에서 오류가 발생하지 않는지 살핀다.
        user_reg_dic = self._get_user_reg_dic(u'mikkang')
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'mikkang', register_key)

        # 로그인, 로그아웃이 잘 되는지 검사한다
        session_key = self.engine.login_manager.login(u'mikkang', u'mikkang', u'143.248.234.140')
        self.engine.login_manager.logout(session_key)

        # 이미 등록한 사용자를 다시 등록할 수 없는지 확인한다
        try:
            self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            self.fail("Though user mikkang already added, registration of same user must be forbidden.")
        except InvalidOperation:
            pass

        # SYSOP 이라는 이름의 사용자는 등록할 수 없다.
        user_reg_dic = self._get_user_reg_dic(u"SYSOP")
        try:
            self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            self.fail("One must not be able to register as using keyword [SYSOP]")
        except InvalidOperation:
            pass

        # TODO: SYSOP 을 닉네임에 사용하면?

    def test_get_info(self):
        self._register_and_confirm(u"combacsa")

        # 로그인된 상태에서 사용자 정보 확인에 성공한다
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        member = self.engine.member_manager.get_info(unicode(session_key))
        self.assertEqual(True, member.activated)
        self.assertEqual(u"combacsa@kaist.ac.kr", member.email)
        self.assertEqual(u"combacsa", member.nickname)
        self.assertEqual(0, member.widget)
        self.assertEqual(0, member.layout)
        self.assertEqual(u"Daejeon", member.campus)

        # 로그아웃된 상태에서 사용자 정보 확인에 실패한다
        self.engine.login_manager.logout(session_key)
        try:
            self.engine.member_manager.get_info(unicode(session_key))
            self.fail("When the session is not logged in, get_info() must fail.")
        except NotLoggedIn:
            pass

    def test_modify_password(self):
        self._register_and_confirm("combacsa")

        # combacsa 사용자의 비밀번호를 computer 로 바꾼다
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        user_password_dic = {'username':u'combacsa', 'current_password':u'combacsa', 'new_password':u'computer'}
        self.engine.member_manager.modify_password(session_key, UserPasswordInfo(**user_password_dic))
        self.engine.login_manager.logout(session_key)

        # 비밀번호가 combacsa 가 아니므로 로그인에 실패해야 한다
        try:
            session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
            self.fail("Login with wrong password must not be permitted")
        except InvalidOperation:
            pass

        # 바꾼 비밀번호로 로그인에 성공한다
        session_key = self.engine.login_manager.login(u'combacsa', u'computer', u'143.248.234.145')
        self.engine.login_manager.logout(session_key)

        # 로그인하지 않은 사용자의 비밀번호를 바꾸는 데 실패한다
        user_password_dic = {'username':u'combacsa', 'current_password':u'computer', 'new_password':u'combacsa'}
        try:
            self.engine.member_manager.modify_password(session_key, UserPasswordInfo(**user_password_dic))
            self.fail("Modify_password must fail when not logged in")
        except NotLoggedIn:
            pass

    def test_modify_password_sysop(self):
        self._register_and_confirm("combacsa")
        session_key_sysop = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'127.0.0.1')

        # Test 1. SYSOP change pasword for user 'combacsa' successfully.
        user_password_dic = {'username':u'combacsa', 'current_password':u'', 'new_password':u'computer'}
        self.engine.member_manager.modify_password_sysop(session_key_sysop, UserPasswordInfo(**user_password_dic))
        # Test 1-1. combacsa can't login with old password
        try:
            session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
            self.fail('Though sysop changed password, user was able to login with old password.')
        except InvalidOperation:
            pass
        # Test 1-2. combacsa can login with new password
        session_key = self.engine.login_manager.login(u'combacsa', u'computer', u'143.248.234.145')
        # Test 2. Anyone who is not SYSOP can't call modify_password_sysop even if it is about user oneself.
        user_password_dic = {'username':u'combacsa', 'current_password':u'', 'new_password':u'combacsa'}
        try:
            self.engine.member_manager.modify_password_sysop(session_key, UserPasswordInfo(**user_password_dic))
            self.fail("Someone who was not a sysop successfully changed one's password.")
        except InvalidOperation:
            pass
        # Test 3. 존재하지 않는 사용자의 비밀번호는 바꾸지 못한다
        user_password_dic = {'username':u'hodduc', 'current_password':u'hodduc', 'new_password':u'hodduci'}
        try:
            self.engine.member_manager.modify_password_sysop(session_key_sysop, UserPasswordInfo(**user_password_dic))
            self.fail("SYSOP can't modify password of nonexisting user")
        except InvalidOperation:
            pass

    def test_modify_user(self):
        self._register_and_confirm(u"combacsa")
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')

        # 사용자 정보를 바꾸고 get_info 로 변화된 것을 확인한다
        modify_user_reg_dic = { 'nickname':u'iamcombacsa', 'signature':u'Philosophy Major', 'self_introduction':u'SPARCSian', 'default_language':u'korean', 'campus':u'Seoul', 'widget':1, 'layout':u'aaa' , 'listing_mode': 0}
        self.engine.member_manager.modify_user(session_key, UserModification(**modify_user_reg_dic))
        member = self.engine.member_manager.get_info(unicode(session_key))
        self.assertEqual(1, member.widget)
        self.assertEqual(u"aaa", member.layout)
        self.assertEqual(u"iamcombacsa", member.nickname)
        self.assertEqual(u"Philosophy Major", member.signature)
        self.assertEqual(u"SPARCSian", member.self_introduction)
        self.assertEqual(u"korean", member.default_language)
        self.assertEqual(u"Seoul", member.campus)
        self.assertEqual(0, member.listing_mode)

        self.engine.login_manager.logout(session_key)

        # 로그인하지 않았으면 사용자 정보를 바꾸지 못한다
        try:
            self.engine.member_manager.modify_user(session_key, UserModification(**modify_user_reg_dic))
            self.fail("Modify user must not be permitted when not logged in.")
        except NotLoggedIn:
            pass

    def test_search_user(self):
        self._register_and_confirm(u"combacsa", {"nickname": u"pipoket"})
        self._register_and_confirm(u"serialx")
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')

        # serialx 로 검색하면 serialx 유저만 검색되어야 한다
        users = self.engine.member_manager.search_user(session_key, u'serialx')
        self.assertEqual(1, len(users))
        self.assertEqual(u"serialx", users[0].username)
        self.assertEqual(u"serialx", users[0].nickname)

        # serialx 라는 닉네임을 갖는 pipoket 유저를 추가하고 둘 다 검색되는지 확인
        self._register_and_confirm(u"pipoket", {"nickname": u"serialx"})
        users = self.engine.member_manager.search_user(session_key, u'serialx')
        self.assertEqual(2, len(users))
        if (users[0].username == 'serialx'): # not sure about order
            users[0], users[1] = users[1], users[0]
        self.assertEqual(u"pipoket", users[0].username)
        self.assertEqual(u"serialx", users[0].nickname)
        self.assertEqual(u"serialx", users[1].username)
        self.assertEqual(u"serialx", users[1].nickname)

        # username 파라메터를 주면 pipoket 은 검색되지 않아야 한다
        users = self.engine.member_manager.search_user(session_key, u'serialx', u'username')
        self.assertEqual(1, len(users))
        self.assertEqual(u"serialx", users[0].username)
        self.assertEqual(u"serialx", users[0].nickname)

        # nickname 파라메터를 주면 combacsa 만 검색되어야 한다
        users = self.engine.member_manager.search_user(session_key, u'pipoket', u'nickname')
        self.assertEqual(1, len(users))
        self.assertEqual(u"combacsa", users[0].username)
        self.assertEqual(u"pipoket", users[0].nickname)

        # 존재하지 않는 사용자로 검색하면 ...
        users = self.engine.member_manager.search_user(session_key, u"hodduc")
        self.assertEqual(0, len(users))

        # username, nickname 도 아닌 이상한 걸 기준으로 검색할 수는 없다
        self.engine.login_manager.logout(session_key)
        try:
            self.engine.member_manager.search_user(session_key, u'mikkang', u'wrong_key')
            self.fail("Must specify correct search key (nickname or username)")
        except InvalidOperation:
            pass

    def test_remove_user(self):
        # XXX(serialx): User remove temp. removed.
        # 현재는 사용자 제거 기능이 동작하지 않는다.
        self._register_and_confirm(u"combacsa")
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        try:
            self.engine.member_manager.remove_user(session_key)
            self.fail("remove_user must fail")
        except InvalidOperation:
            pass

    def test_is_sysop(self):
        # Not a sysop
        self._register_and_confirm(u"combacsa")
        session_key_combacsa = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        self.assertEqual(False, self.engine.member_manager.is_sysop(session_key_combacsa))

        # A sysop
        session_key_sysop = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'143.248.234.145')
        self.assertEqual(True, self.engine.member_manager.is_sysop(session_key_sysop))

    def test_backdoor_confirm(self):
        self._register_user(u"combacsa")

        # SYSOP 은 backdoor confirm 을 행할 수 있다.
        session_key_sysop = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'143.248.234.145')
        self.engine.member_manager.backdoor_confirm(session_key_sysop, u'combacsa')
        # confirm 된 user 가 로그인에 성공한다
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.140')

        # SYSOP 이 아닌 user 는 backdoor_confirm 을 쓸 수 없다
        self._register_user(u"hodduc")
        try:
            self.engine.member_manager.backdoor_confirm(session_key, u"hodduc")
            self.fail("backdoor_confirm can't be performed by someone who is not SYSOP")
        except InvalidOperation:
            pass

    def test_authenticate(self):
        self._register_and_confirm(u"combacsa")
        # 인증 성공

        self.assertEqual(u"combacsa", self.engine.member_manager.authenticate(u'combacsa', u'combacsa', u'143.248.234.140').nickname)
        # 인증 실패 - wrong passwd
        try:
            self.engine.member_manager.authenticate(u'combacsa', u'mikkang', u'143.248.234.140')
            self.fail("must raise exception when authenticate with wrong Password")
        except InvalidOperation:
            pass
        # 인증 실패 - wrong username
        try:
            self.engine.member_manager.authenticate(u'elaborate', u'elaborate', u'143.248.234.140')
            self.fail("must not be able to authenticate with user who is not exist")
        except InvalidOperation:
            pass

        self._register_user(u"hodduc")
        # 인증 실패 - not activated
        try:
            self.engine.member_manager.authenticate(u'hodduc', u'hodduc', u'143.248.234.140')
            self.fail("Not activated user must not be able to authenticate")
        except InvalidOperation:
            # XXX 실패 사유가 무엇인지 확인할 수 있어야 한다 ...
            pass

        # 공백 문자로 로그인이 가능해서는 안 됨 (보안 허점)
        try:
            self.engine.member_manager.authenticate(u" ", u" ", u"143.248.234.140")
            self.fail("Username ' ' must not be able to log-in")
        except InvalidOperation:
            pass

    def test_user_to_sysop(self):
        self._register_and_confirm(u"combacsa")
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        #Prevent user from using user_to_sysop
        try:
            self.engine.member_manager.user_to_sysop(session_key, u'combacsa')
            self.fail("Non-SYSOP cannot call user_to_sysop")
        except InvalidOperation:
            pass

        session_key = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'127.0.0.1')
        self.engine.member_manager.user_to_sysop(session_key, u'combacsa')
        self.engine.login_manager.logout(session_key)
        
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        #check if user is not SYSOP
        self.assertEqual(True, self.engine.member_manager.is_sysop(session_key))

        # TODO: 이미 시삽인 사용자를 시삽으로 임명하는 경우

    def test_authenticate_mode(self):
        self._register_and_confirm(u"combacsa")
        session_key = self.engine.login_manager.login(u'combacsa',u'combacsa', u'143.248.234.154')
        check_mode= self.engine.member_manager.authentication_mode(session_key)
        # 아직 인증단계를 유저별로 나누는 것이 구현이 안되어있기 때문에 기본값 0이 리턴됩니다.
        self.assertEqual(0, check_mode)

    def test_query_by_username(self):
        self._register_and_confirm(u"combacsa")
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        # query about combacsa
        result = self.engine.member_manager.query_by_username(session_key, u'combacsa')
        # TODO: 다른 test 참고하여 to_dict 를 만들고 거기에 맞춰서 딕셔너리로 테스트하게 수정
        self.assertEqual(PublicUserInformation(username=u'combacsa', last_logout_time=0, self_introduction=u'combacsa', last_login_ip=u'143.248.234.145', signature=u'combacsa', campus=u'Daejeon', nickname=u'combacsa', email=u'combacsa@kaist.ac.kr'), result)

        # query about nonexisting member
        try:
            result = self.engine.member_manager.query_by_username(session_key, u'hodduc')
            self.fail('querying about nonexisting user must fail.')
        except InvalidOperation:
            pass
        # TODO: query_by_username 이외에 다른 함수들에 대해서도 테스트 코드 작성

    def test_cancel_confirm(self):
        # 이미 Confirm된 유저의 이메일 인증을 해제하는 기능을 테스트

        # 0. 없는 유저에 대해 cancel_confirm 시도. Exception이 발생해야 정상
        try:
            self.engine.member_manager.cancel_confirm(u'hodduc')
            self.fail('Not exist user cannot be canceled')
        except:
            pass

        # 1. 유저 hodduc을 추가
        register_key = self._register_user(u"hodduc")

        # 2. 아직 confirm되지 않은 상태로 cancel_confirm 시도. Exception이 발생해야 정상
        try:
            self.engine.member_manager.cancel_confirm(u'hodduc')
            self.fail('Not confirmed user shouldn`t be canceled')
        except:
            pass

        # 3. Confirm 후 로그인/로그아웃 성공
        self.engine.member_manager.confirm(u'hodduc', unicode(register_key))
        session_key = self.engine.login_manager.login(u'hodduc', u'hodduc', u'143.248.234.140')
        self.engine.login_manager.logout(session_key)

        # 4. Confirm Cancel 후 로그인. Exception이 발생해야 정상
        self.engine.member_manager.cancel_confirm(u'hodduc')
        try:
            session_key = self.engine.login_manager.login(u'hodduc', u'hodduc', u'143.248.234.140')
            self.fail('This user must not login because he canceled his confirm')
        except InvalidOperation:
            pass

        # 5. 옛날 register_key로 confirm이 되는지 확인. 안 되어야 정상
        try:
            self.engine.member_manager.confirm(u'hodduc', unicode(register_key))
            self.fail('This activation key is invalid')
        except InvalidOperation:
            pass

        # 6. 다른 사용자가 정상적으로 hodduc@kaist.ac.kr으로 가입, 인증, 로그인 할 수 있는지 확인
        self._register_and_confirm(u"sillo", {"email": u"hodduc@kaist.ac.kr"})
        session_key = self.engine.login_manager.login(u'sillo', u'sillo', u'143.248.234.140')
        self.engine.login_manager.logout(session_key)

    def test_change_listing_mode(self):
        self._register_and_confirm(u"combacsa")
        session_key = self.engine.login_manager.login(u"combacsa", u"combacsa", "127.0.0.1")
        # 기본값은 0
        session = arara.model.Session()
        sa_object = self.engine.member_manager._get_user_by_session(session, session_key)
        self.assertEqual(0, sa_object.listing_mode)
        session.close()
        # 변화 후 값 변화 학인
        self.engine.member_manager.change_listing_mode(session_key, 1)
        session = arara.model.Session()
        sa_object = self.engine.member_manager._get_user_by_session(session, session_key)
        self.assertEqual(1, sa_object.listing_mode)
        session.close()
        # 이상한 값으로 변화 금지
        try:
            self.engine.member_manager.change_listing_mode(session_key, 3)
            self.fail("successfully changed listing mode into wrong number")
        except InvalidOperation:
            pass

    def test_get_listing_mode(self):
        self._register_and_confirm(u"combacsa")
        session_key = self.engine.login_manager.login(u"combacsa", u"combacsa", "127.0.0.1")
        self.assertEqual(0, self.engine.member_manager.get_listing_mode(session_key))
        # change 후에도 반영되는가
        self.engine.member_manager.change_listing_mode(session_key, 1)
        self.assertEqual(1, self.engine.member_manager.get_listing_mode(session_key))

    def test_get_selected_boards(self): 
        session_key = self.engine.login_manager.login(u"SYSOP", u"SYSOP", "127.0.0.1")
        self.engine.board_manager.add_board(session_key, 'testboard0', 'testboard0', 'board0 for test')
        self.engine.board_manager.add_board(session_key, 'testboard1', 'testboard1', 'board1 for test')
        self.engine.board_manager.add_board(session_key, 'testboard2', 'testboard2', 'board2 for test')
        board0 = self.engine.board_manager.get_board('testboard0')
        board1 = self.engine.board_manager.get_board('testboard1')
        board2 = self.engine.board_manager.get_board('testboard2')
        self.engine.member_manager.set_selected_boards(session_key,[board0.id,board1.id,board2.id])
        board_name_set=set([board.board_name for board in self.engine.member_manager.get_selected_boards(session_key)])
        self.assertEqual(set(('testboard0', 'testboard1', 'testboard2')), board_name_set)

    def test_set_selected_boards(self): 
        session = arara.model.Session()
        session_key = self.engine.login_manager.login(u"SYSOP", u"SYSOP", "127.0.0.1")
        self.engine.board_manager.add_board(session_key, 'testboard0', 'testboard0', 'board0 for test')
        self.engine.board_manager.add_board(session_key, 'testboard1', 'testboard1', 'board1 for test')
        self.engine.board_manager.add_board(session_key, 'testboard2', 'testboard2', 'board2 for test')
        board0 = self.engine.board_manager.get_board('testboard0')
        board1 = self.engine.board_manager.get_board('testboard1')
        board2 = self.engine.board_manager.get_board('testboard2')
        user = self.engine.member_manager._get_user_by_session(session, session_key)
        self.engine.member_manager.set_selected_boards(session_key,[board0.id,board1.id,board2.id])
        print '\nsetting is done'
        board_id_set=set()
        for selected_board in session.query(arara.model.SelectedBoards).filter_by(user_id=user.id).all():
            board_id_set.add(selected_board.board.id)
        
        self.assertEqual(set((board0.id,board1.id,board2.id)),board_id_set)

    def test_blocking_non_kaist_email(self):
        # Try to register one user, richking, with non-kaist e-mail address, but faking as if it is KAIST e-mail
        user_reg_dic = self._get_user_reg_dic(u'richking', {'email': 'richking@example.com (@kaist.ac.kr'})
        try:
            self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            self.fail("non-kaist email address must not be able to register.")
        except InvalidOperation:
            pass

        # KAIST E-Mail 주소의 길이제한 (4-20) 을 기준으로 한 경계값 검증
        user_reg_dic = self._get_user_reg_dic(u'richking', {'email': 'a@kaist.ac.kr'})
        try:
            self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            self.fail("too short KAIST email address must not be allowed.")
        except InvalidOperation:
            pass

        user_reg_dic = self._get_user_reg_dic(u'richking', {'email': 'abcdefghijklmnopqrstuvwxyz@kaist.ac.kr'})
        try:
            self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            self.fail("too long KAIST email address must not be allowed.")
        except InvalidOperation:
            pass

    def test_blocking_invalid_email_address(self):
        # @ 의 갯수가 2 개
        user_reg_dic = self._get_user_reg_dic(u'richking', {'email': 'richking@@kaist.ac.kr'})
        try:
            self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            self.fail("Allowed EMail address must not contain more than one @.")
        except InvalidOperation:
            pass

        # @ 의 갯수가 0 개
        user_reg_dic = self._get_user_reg_dic(u'richking', {'email': 'sparcs.kaist.ac.kr'})
        try:
            register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            self.fail("Allowed EMail address must contain exactly one @.")
        except InvalidOperation:
            pass

        # E-Mail 주소에 허용되지 않는 문자 ([]) 포함
        user_reg_dic = self._get_user_reg_dic(u'richking', {'email': '[hello]@kaist.ac.kr'})
        try:
            self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            self.fail("Allowed EMail address must not contain any of [, ], \\")
        except InvalidOperation:
            pass
        
    def tearDown(self):
        # Common tearDown
        super(MemberManagerTest, self).tearDown()
    
def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MemberManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
