# -*- coding: utf-8 -*-
import xmlrpclib

from arara.util import require_login, filter_dict
from arara import model

READ_ARTICLE_WHITELIST = ('id', 'title', 'content', 'last_modified_date', 'deleted', 'blacklisted', 'author_username', 'vote', 'date', 'hit', 'depth', 'root_id', 'is_searchable')
api_server_address = 'http://nan.sparcs.org:9000/api'
api_key = '54ebf56de7684dba0d69bffc9702e1b4'

class SearchManager(object):
    '''
    K-Search에 현재 게시물들을 추가하는 클래스
    '''

    def __init__(self):
        pass

    def _get_dict(self, item, whitelist=None):
        item_dict = item.__dict__
        if item_dict.has_key('author_id'):
            item_dict['author_username'] = item.author.username
            del item_dict['author_id']
        if item_dict.has_key('board_id'):
            item_dict['board_name'] = item.board.board_name
            del item_dict['board_id']
        if item_dict.has_key('root_id'):
            if not item_dict['root_id']:
                item_dict['root_id'] = item_dict['id']
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

if __name__ == "__main__":
    pass
