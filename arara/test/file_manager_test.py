#-*- coding: utf:-8 -*-
import unittest
import os
import sys
import time

thrift_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gen-py'))
sys.path.append(thrift_path)
arara_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(arara_path)

from arara.test.test_common import AraraTestBase
from arara_thrift.ttypes import *
import arara.model


class FileManagerTest(AraraTestBase):
    def setUp(self):
        # Common preparation for all tests
        super(FileManagerTest, self).setUp(stub_time=True, stub_time_initial=1.1)

        # Login as SYSOP and create 'garbage'
        session_key_sysop = self.engine.login_manager.login(
                u'SYSOP', u'SYSOP', u'123.123.123.123')
        self.engine.board_manager.add_board(
                unicode(session_key_sysop), u'garbages', u'쓰레기가 모이는 곳', u'Garbage Board')

        # Register mikkang for test
        self.mikkang_session_key = self.register_and_login(u'mikkang')

        # Write an article for filemanager test
        article_dict = {'title': u'serialx is...', 'content': u'polarbear', 'heading': u''}
        self.engine.article_manager.write_article(self.mikkang_session_key, 
                u'garbages', WrittenArticle(**article_dict))
        # Article to test filemanager has no 1
        self.article_id = 1
    
    def save_file(self):
        fileinfo = self.engine.file_manager.save_file(
                self.mikkang_session_key, self.article_id , u'hahahah.jpg')
        self.assertEqual(u'garbages/1970/1/1', fileinfo.file_path)
        self.assertEqual(u'2f2bea882ef178d056434f5cdb0d0909', 
                         fileinfo.saved_filename)

    def download_file(self):
        ret = self.engine.file_manager.download_file(self.article_id , 1)
        self.assertEqual(u'hahahah.jpg', ret.real_filename)
        self.assertEqual(u'garbages/1970/1/1', ret.file_path)
        self.assertEqual(u'2f2bea882ef178d056434f5cdb0d0909', ret.saved_filename)

    def delete_file(self):
        fileinfo = self.engine.file_manager.delete_file(self.mikkang_session_key, 
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

    def test__get_attached_file_list(self):
        # 파일이 있는 경우
        fileinfo = self.engine.file_manager.save_file(
                self.mikkang_session_key, self.article_id , u'hahahah.jpg')
        result = self.engine.file_manager._get_attached_file_list(self.article_id)
        self.assertEqual(1, len(result))
        self.assertEqual(u'hahahah.jpg', result[0].filename)
        self.assertEqual(1, result[0].file_id)

        # 파일이 없는 경우
        result = self.engine.file_manager._get_attached_file_list(self.article_id + 3)
        self.assertEqual(0, len(result))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FileManagerTest)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
