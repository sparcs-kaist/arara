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

        # Regiister one user, combacsa
        user_reg_dic = {'username':u'combacsa', 'password':u'combacsa', 'nickname':u'combacsa', 'email':u'combacsa@kaist.ac.kr', 'signature':u'combacsa', 'self_introduction':u'combacsa', 'default_language':u'english', 'campus':u'Daejeon'}
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'combacsa', unicode(register_key))

        # Register one user, serialx(with campus=null)
        user_reg_dic = {'username':u'serialx', 'password':u'serialx', 'nickname':u'serialx', 'email':u'serialx@kaist.ac.kr', 'signature':u'serialx', 'self_introduction':u'serialx', 'default_language':u'english', 'campus':u''}
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'serialx', unicode(register_key))

        # Register one user, pipoket, but not confirm.
        user_reg_dic = {'username':u'pipoket', 'password':u'pipoket', 'nickname':u'pipoket', 'email':u'pipoket@kaist.ac.kr', 'signature':u'pipoket', 'self_introduction':u'pipoket', 'default_language':u'english', 'campus':u'Daejeon'}
        self.register_key_pipoket = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))

    def testAddUserWithoutConfirm(self):
        user_reg_dic = {'username':u'hodduc', 'password':u'hodduc', 'nickname':u'hodduc', 'email':u'hodduc@kaist.ac.kr', 'signature':u'hodduc', 'self_introduction':u'hodduc', 'default_language':u'english', 'campus':u'Daejeon' }
        # _register_without_confirm 함수로 가입 후 로그인
        # 만약 원래 의도대로 Self Activation되지 않았다면 login이 되지 않을 것이므로 Exception이 발생함
        self.engine.member_manager._register_without_confirm(user_reg_dic, False)
        session_key = self.engine.login_manager.login(u'hodduc', u'hodduc', u'143.248.234.140')

        user_reg_dic = {'username':u'sillo', 'password':u'sillo', 'nickname':u'sillo', 'email':u'sillo@kaist.ac.kr', 'signature':u'sillo', 'self_introduction':u'sillo', 'default_language':u'english', 'campus':u'Daejeon'}
        # _register_without_confirm 함수로 시삽 권한으로 가입 후 로그인
        # 시삽 권한을 가지는지 확인
        self.engine.member_manager._register_without_confirm(user_reg_dic, True)
        session_key = self.engine.login_manager.login(u'sillo', u'sillo', u'143.248.234.140')
        if not self.engine.member_manager.is_sysop(session_key):
            self.fail('_register_without_confirm() failed! :: Failed to grant SYSOP previlege')



    def testAddMikkang(self):
        user_reg_dic = {'username':u'mikkang', 'password':u'mikkang', 'nickname':u'mikkang', 'email':u'mikkang@kaist.ac.kr', 'signature':u'mikkang', 'self_introduction':u'mikkang', 'default_language':u'english', 'campus':u'Daejeon' }
        # Check this user is not yet registered
        self.assertEqual(False, self.engine.member_manager.is_registered(user_reg_dic['username']))
        self.assertEqual(False, self.engine.member_manager.is_registered_nickname(user_reg_dic['nickname']))
        self.assertEqual(False, self.engine.member_manager.is_registered_email(user_reg_dic['email']))

        # Register the user, login, and check if any problem occurs
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'mikkang', register_key)
        session_key = self.engine.login_manager.login(u'mikkang', u'mikkang', u'143.248.234.140')
        self.engine.login_manager.logout(session_key)

    def testNotAddSerialx(self):
        # XXX(combacsa): Implement Later
        pass

    def testViewCombacsa(self):
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        member = self.engine.member_manager.get_info(unicode(session_key))
        self.assertEqual(True, member.activated)
        self.assertEqual(u"combacsa@kaist.ac.kr", member.email)
        self.assertEqual(u"combacsa", member.nickname)
        self.assertEqual(0, member.widget)
        self.assertEqual(0, member.layout)
        self.assertEqual(u"Daejeon", member.campus)
        self.engine.login_manager.logout(session_key)

    def testPasswdChange(self):
        # Change password, and then login again to check it applied
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        user_password_dic = {'username':u'combacsa', 'current_password':u'combacsa', 'new_password':u'computer'}
        self.engine.member_manager.modify_password(session_key, UserPasswordInfo(**user_password_dic))
        self.engine.login_manager.logout(session_key)
        try:
            session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
            fail()
        except InvalidOperation:
            pass
        session_key = self.engine.login_manager.login(u'combacsa', u'computer', u'143.248.234.145')
        # Change password again to let it be untouched
        user_password_dic = {'username':u'combacsa', 'current_password':u'computer', 'new_password':u'combacsa'}
        self.engine.member_manager.modify_password(session_key, UserPasswordInfo(**user_password_dic))
        self.engine.login_manager.logout(session_key)

    def testPasswdChangeSysop(self):
        # Preparation
        session_key_sysop = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'127.0.0.1')
        # Test 1. SYSOP change pasword for user 'combacsa' successfully.
        user_password_dic = {'username':u'combacsa', 'current_password':u'', 'new_password':u'computer'}
        self.engine.member_manager.modify_password_sysop(session_key_sysop, UserPasswordInfo(**user_password_dic))
        # Test 1-1. combacsa can't login with old password
        session_key = None
        try:
            session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
            self.fail('Though sysop changed password, user was able to login with old password.')
        except InvalidOperation:
            pass
        # Test 1-2. combacsa can login with new password
        session_key = self.engine.login_manager.login(u'combacsa', u'computer', u'143.248.234.145')
        # Test 2. Anyone except SYSOP can't call modify_password_sysop even if it is user oneself.
        user_password_dic = {'username':u'combacsa', 'current_password':u'', 'new_password':u'combacsa'}
        try:
            self.engine.member_manager.modify_password_sysop(session_key, UserPasswordInfo(**user_password_dic))
            self.fail("Someone who was not a sysop successfully changed one's password.")
        except InvalidOperation:
            pass

    def testModifyInfo(self):
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        modify_user_reg_dic = { 'nickname':u'combacsa is sysop', 'signature':u'KAIST07 && HSHS07 && SPARCS07', 'self_introduction':u'i am Kyuhong', 'default_language':u'korean', 'campus':u'Seoul', 'widget':1, 'layout':u'aaa' , 'listing_mode': 0}
        self.engine.member_manager.modify_user(session_key, UserModification(**modify_user_reg_dic))
        member = self.engine.member_manager.get_info(unicode(session_key))
        self.assertEqual(1, member.widget)
        self.assertEqual(u"aaa", member.layout)
        self.assertEqual(u"combacsa is sysop", member.nickname)
        self.assertEqual(u"KAIST07 && HSHS07 && SPARCS07", member.signature)
        self.assertEqual(u"i am Kyuhong", member.self_introduction)
        self.assertEqual(u"korean", member.default_language)
        self.assertEqual(u"Seoul", member.campus)
        self.assertEqual(0, member.listing_mode)

        # TODO: 이 아래 3줄 왜 필요하지?
        # Restore change (at least nickname)
        modify_user_reg_dic = { 'nickname':u'combacsa', 'signature':u'KAIST07 && HSHS07 && SPARCS07', 'self_introduction':u'i am Kyuhong', 'default_language':u'korean', 'campus':u'Seoul', 'widget':1, 'layout':u'aaa' }
        self.engine.member_manager.modify_user(session_key, UserModification(**modify_user_reg_dic))
        self.engine.login_manager.logout(session_key)

    def testSearch(self):
        # Single User Result
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        users = self.engine.member_manager.search_user(session_key, u'serialx')
        self.assertEqual(1, len(users))
        self.assertEqual(u"serialx", users[0].username)
        self.assertEqual(u"serialx", users[0].nickname)
        # Multi User Result (Add new user with duplicated nickname)
        user_reg_dic = {'username':u'ggingkkang', 'password':u'xx', 'nickname':u'serialx', 'email':u'ggingkkang@kaist.ac.kr', 'signature':u'', 'self_introduction':u'', 'default_language':u'english', 'campus':u'Seoul' }
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'ggingkkang', unicode(register_key))

        users = self.engine.member_manager.search_user(session_key, u'serialx')
        self.assertEqual(2, len(users))
        if (users[0].username == 'serialx'): # not sure about order
            self.assertEqual(u"serialx", users[0].username)
            self.assertEqual(u"serialx", users[0].nickname)
            self.assertEqual(u"ggingkkang", users[1].username)
            self.assertEqual(u"serialx", users[1].nickname)
        else:
            self.assertEqual(u"serialx", users[1].username)
            self.assertEqual(u"serialx", users[1].nickname)
            self.assertEqual(u"ggingkkang", users[0].username)
            self.assertEqual(u"serialx", users[0].nickname)

        users = self.engine.member_manager.search_user(session_key, u'ggingkkang', u'username')
        self.assertEqual(1, len(users))
        self.assertEqual(u"ggingkkang", users[0].username)
        self.assertEqual(u"serialx", users[0].nickname)

        users = self.engine.member_manager.search_user(session_key, u'combacsa', u'nickname')
        self.assertEqual(1, len(users))
        self.assertEqual(u"combacsa", users[0].username)
        self.assertEqual(u"combacsa", users[0].nickname)

        try:
            self.engine.member_manager.search_user(session_key, u'mikkang', u'wrong_key')
            fail()
        except InvalidOperation:
            pass
        self.engine.login_manager.logout(session_key)

        # 찾는 사람이 없는 경우에는?

    def testRemove(self):
        # XXX(serialx): User remove temp. removed.
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        try:
            self.engine.member_manager.remove_user(session_key)
            fail()
        except InvalidOperation:
            pass

    def testSysop(self):
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        self.assertEqual(False, self.engine.member_manager.is_sysop(session_key))
        self.engine.login_manager.logout(session_key)
        session_key = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'143.248.234.145')
        self.assertEqual(True, self.engine.member_manager.is_sysop(session_key))
        self.engine.login_manager.logout(session_key)
        # Prevent adding SYSOP
        user_reg_dic = { 'username':u'SYSOP', 'password':u'SYSOP', 'nickname':u'SYSOP', 'email':u'SYSOP@sparcs.org', 'signature':u'', 'self_introduction':u'i am mikkang', 'default_language':u'english', 'campus':u'' }
        try:
            sysop_register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            fail()
        except InvalidOperation:
            pass

    def testBackdoorConfirm(self):
        user_reg_dic = {'username':u'mikkang20', 'password':u'mikkang', 'nickname':u'mikkang20', 'email':u'mikkang20@kaist.ac.kr', 'signature':u'mikkang', 'self_introduction':u'mikkang', 'default_language':u'english', 'campus':u'' }
        registration_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        session_key = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'143.248.234.145')
        self.engine.member_manager.backdoor_confirm(session_key, u'mikkang20')
        self.engine.login_manager.logout(session_key)
        session_key = self.engine.login_manager.login(u'mikkang20', u'mikkang', u'143.248.234.140')
        self.engine.login_manager.logout(session_key)
        # XXX 시삽이 아닌 사람이 백도어 컨펌을 못 하는 것을 테스트.

    def testAuthenticate(self):
        # 인증 성공
        msg1 = self.engine.member_manager.authenticate(u'combacsa', u'combacsa', u'143.248.234.140')
        msg2 = self.engine.member_manager.authenticate(u'serialx',  u'serialx', u'143.248.234.140')
        # 인증 실패 - wrong passwd
        try:
            msg3 = self.engine.member_manager.authenticate(u'combacsa', u'mikkang', u'143.248.234.140')
        except InvalidOperation:
            pass
        # 인증 실패 - wrong username
        try:
            msg4 = self.engine.member_manager.authenticate(u'elaborate', u'elaborate', u'143.248.234.140')
        except InvalidOperation:
            pass
        # 인증 실패 - not activated
        try:
            msg5 = self.engine.member_manager.authenticate(u'pipoket', u'pipoket', u'143.248.234.140')
        except InvalidOperation:
            # XXX 실패 사유가 무엇인지 확인할 수 있어야 한다 ...
            pass
        try:
            msg6 = self.engine.member_manager.authenticate(u" ", u" ", u"143.248.234.140")
            self.fail()
        except InvalidOperation:
            pass

    def testUserToSysop(self):
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        #Prevent user from using user_to_sysop
        try:
            self.engine.member_manager.user_to_sysop(session_key, u'combacsa')
            self.fail()
        except InvalidOperation:
            pass

        session_key = self.engine.login_manager.login(u'SYSOP', u'SYSOP', u'127.0.0.1')
        self.engine.member_manager.user_to_sysop(session_key, u'combacsa')
        self.engine.login_manager.logout(session_key)
        
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        #check if user is not SYSOP
        self.assertEqual(True, self.engine.member_manager.is_sysop(session_key))

    def testAuthenticationMode(self):
        session_key = self.engine.login_manager.login(u'combacsa',u'combacsa', u'143.248.234.154')
        check_mode= self.engine.member_manager.authentication_mode(session_key)
        # 아직 인증단계를 유저별로 나누는 것이 구현이 안되어있기 때문에 기본값 0이 리턴됩니다.
        self.assertEqual(0, check_mode)

    def test_query_by_username(self):
        session_key = self.engine.login_manager.login(u'combacsa', u'combacsa', u'143.248.234.145')
        # query about combacsa
        result = self.engine.member_manager.query_by_username(session_key, u'combacsa')
        # TODO: 다른 test 참고하여 to_dict 를 만들고 거기에 맞춰서 딕셔너리로 테스트하게 수정
        self.assertEqual(PublicUserInformation(username=u'combacsa', last_logout_time=0, self_introduction=u'combacsa', last_login_ip=u'143.248.234.145', signature=u'combacsa', campus=u'Daejeon', nickname=u'combacsa', email=u'combacsa@kaist.ac.kr'), result)

        # query about nonexisting member
        try:
            result = self.engine.member_manager.query_by_username(session_key, u'unknonw')
            self.fail('querying about nonexisting user must fail.')
        except InvalidOperation:
            pass
        # TODO: query_by_username 이외에 다른 함수들에 대해서도 테스트 코드 작성

    def test_cancel_confirm(self):
        # 이미 Confirm된 유저의 이메일 인증을 해제하는 기능을 테스트

        # 0. 없는 유저에 대해 cancel_confirm 시도. Exception이 발생해야 정상
        try:
            self.engine.member_manager.cancel_confirm(u'ghost_member')
            self.fail('Not exist user cannot be canceled')
        except:
            pass

        # 1. 유저 hodduc을 추가
        user_reg_dic = {'username':u'hodduc', 'password':u'hodduc',
                'nickname':u'hodduc', 'email':u'hodduc@kaist.ac.kr',
                'signature':u'hodduc', 'self_introduction':u'hodduc',
                'default_language':u'english', 'campus':u'Daejeon' }
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))

        # 2. 아직 confirm되지 않은 상태로 cancel_confirm 시도. Exception이 발생해야 정상
        try:
            self.engine.member_manager.cancel_confirm(u'hodduc')
            self.fail('Not confirmed user shouldn`t be canceled')
        except:
            pass

        # 3. Confirm 후 로그인/로그아웃
        self.engine.member_manager.confirm(u'hodduc', unicode(register_key))
        session_key = self.engine.login_manager.login(u'hodduc', u'hodduc', u'143.248.234.140')
        self.engine.login_manager.logout(session_key)

        # 4. Confirm Cancel 후 로그인. Exception이 발생해야 정상
        self.engine.member_manager.cancel_confirm(u'hodduc')
        try:
            session_key = self.engine.login_manager.login(u'hodduc', u'hodduc', u'143.248.234.140')
            self.fail('This user must not login because he canceled his confirm')
        except:
            pass

        # 5. 옛날 register_key로 confirm이 되는지 확인. 안 되어야 정상
        try:
            self.engine.member_manager.confirm(u'hodduc', unicode(register_key))
            self.fail('This activation key is invalid')
        except:
            pass

        # 6. 다른 사용자가 정상적으로 hodduc@kaist.ac.kr으로 가입, 인증, 로그인 할 수 있는지 확인
        user_reg_dic = {'username':u'fake_hodduc', 'password':u'fake_hodduc',
                'nickname':u'fake_hodduc', 'email':u'hodduc@kaist.ac.kr',
                'signature':u'fake_hodduc', 'self_introduction':u'fake_hodduc',
                'default_language':u'english', 'campus':u'Daejeon' }
        register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
        self.engine.member_manager.confirm(u'fake_hodduc', unicode(register_key))
        session_key = self.engine.login_manager.login(u'fake_hodduc', u'fake_hodduc', u'143.248.234.140')
        self.engine.login_manager.logout(session_key)


    def test_change_listing_mode(self):
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
        session_key = self.engine.login_manager.login(u"combacsa", u"combacsa", "127.0.0.1")
        self.assertEqual(0, self.engine.member_manager.get_listing_mode(session_key))
        # change 후에도 반영되는가
        self.engine.member_manager.change_listing_mode(session_key, 1)
        self.assertEqual(1, self.engine.member_manager.get_listing_mode(session_key))

    def test_get_selected_boards(self): 
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
        board_name_set=set([board.board_name for board in self.engine.member_manager.get_selected_boards(session_key)])
        
        self.assertEqual(set(('testboard0', 'testboard1', 'testboard2')), board_name_set)
        session.close()

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
        user_reg_dic = {'username':u'richking', 'password':u'richking', 'nickname':u'richking', 'email':u'richking@example.com (@kaist.ac.kr', 'signature':u'richking', 'self_introduction':u'richking', 'default_language':u'english', 'campus':u'Daejeon'}
        try:
            register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            self.fail("non-kaist email address must not be able to register.")
        except InvalidOperation:
            pass

    def test_blocking_invalid_email_address(self):
        # @ 의 갯수가 2 개
        user_reg_dic = {'username':u'richking', 'password':u'richking', 'nickname':u'richking', 'email':u'richking@@kaist.ac.kr', 'signature':u'richking', 'self_introduction':u'richking', 'default_language':u'english', 'campus':u'Daejeon'}
        try:
            register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            self.fail("Allowed EMail address must not contain more than one @.")
        except InvalidOperation:
            pass

        # @ 의 갯수가 0 개
        user_reg_dic = {'username':u'richking', 'password':u'richking', 'nickname':u'richking', 'email':u'sparcs.kaist.ac.kr', 'signature':u'richking', 'self_introduction':u'richking', 'default_language':u'english', 'campus':u'Daejeon'}
        try:
            register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
            self.fail("Allowed EMail address must contain exactly one @.")
        except InvalidOperation:
            pass

        # E-Mail 주소에 허용되지 않는 문자 ([]) 포함
        user_reg_dic = {'username':u'richking', 'password':u'richking', 'nickname':u'richking', 'email':u'[hello]@kaist.ac.kr', 'signature':u'richking', 'self_introduction':u'richking', 'default_language':u'english', 'campus':u'Daejeon'}
        try:
            register_key = self.engine.member_manager.register_(UserRegistration(**user_reg_dic))
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
