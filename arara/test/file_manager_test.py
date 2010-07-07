#-*- coding: utf:-8 -*-
import unittest
import os
import sys
import logging

thrift_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(thrift_path)
arara_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(arara_path)

from arara_thrift.ttypes import *
import arara.model
import arara
import arara.server
import arara.model
server = None

# Time is needed for testing file_manager
import time

class FileManagerTest(unittest.TestCase):
    def setUp(self):
        global server
        # Common preparation for all tests
        logging.basicConfig(level=logging.ERROR)
        arara.model.init_test_database()
        arara.server.server = arara.get_namespace()
        server = arara.get_namespace()

        # Fake time for further test
        def stub_time():
            return 1.1
        self.org_time = time.time
        time.time = stub_time

        # Login as SYSOP and create 'garbage'
        session_key_sysop = server.login_manager.login(
                u'SYSOP', u'SYSOP', u'123.123.123.123')
        server.board_manager.add_board(
                unicode(session_key_sysop), u'garbages', u'Garbage Board')

        # Register mikkang for test
        user_reg_dict = {'username':u'mikkang', 'password':u'mikkang', 
                        'nickname':u'mikkang', 'email':u'mikkang@example.com',
                        'signature':u'mikkang', 'self_introduction':u'mikkang',
                        'default_language':u'english', 'campus':u'Seoul' }
        register_key = server.member_manager.register_(
                UserRegistration(**user_reg_dict))
        server.member_manager.confirm(u'mikkang', unicode(register_key))
        self.mikkang_session_key = server.login_manager.login(
                u'mikkang', u'mikkang', u'143.248.234.140')

        # Write an article for filemanager test
        article_dict = {'title': u'serialx is...', 'content': u'polarbear', 'heading': u''}
        server.article_manager.write_article(self.mikkang_session_key, 
                u'garbages', WrittenArticle(**article_dict))
        # Article to test filemanager has no 1
        self.article_id = 1
    
    def save_file(self):
        fileinfo = server.file_manager.save_file(
                self.mikkang_session_key, self.article_id , u'hahahah.jpg')
        self.assertEqual(u'garbages/1970/1/1', fileinfo.file_path)
        self.assertEqual(u'2f2bea882ef178d056434f5cdb0d0909', 
                         fileinfo.saved_filename)

    def download_file(self):
        ret = server.file_manager.download_file(self.article_id , 1)
        self.assertEqual(u'hahahah.jpg', ret.real_filename)
        self.assertEqual(u'garbages/1970/1/1', ret.file_path)
        self.assertEqual(u'2f2bea882ef178d056434f5cdb0d0909', ret.saved_filename)

    def delete_file(self):
        fileinfo = server.file_manager.delete_file(self.mikkang_session_key, 
                self.article_id , 1)
        self.assertEqual(u'garbages/1970/1/1', fileinfo.file_path)
        self.assertEqual(u'2f2bea882ef178d056434f5cdb0d0909', 
                         fileinfo.saved_filename)

    def test_save_file(self):
        self.save_file()

    def test_download_file(self):
        self.save_file()
        self.download_file()

    def test_delete_file(self):
        self.save_file()
        self.delete_file()

    def tearDown(self):
        arara.model.clear_test_database()
        # Restore the time
        time.time = self.org_time

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FileManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
