#!/usr/bin/python

import xmlrpclib
server = xmlrpclib.Server('http://localhost:8000')
server.article_manager.article_list('00', 'garbages')
server.article_manager.article_list('000123', 'garbages')
user_reg_dic = {'id':'mikkang', 'password':'mikkang', 'nickname':'mikkang', 'email':'mikkang', 'sig':'mikkang', 'self_introduce':'mikkang', 'default_language':'english' }
server.member_manager.register(user_reg_dic)
server.member_manager.confirm('mikkang', 'd49cf5955c13a6589ca1b2149f015e4d')
ret, sess = server.login_manager.login('mikkang', 'mikkang', '12')
article_dic = {'author':'serialx', 'title': 'serialx is...', 'content': 'polarbear', 'method': 'web'}
server.article_manager.write_article(sess, 'garbages', article_dic)
article_dic = {'author':'serialx', 'title': 'polarbear', 'content': 'polarbear', 'method': 'web'}
server.article_manager.write_article(sess, 'garbages', article_dic)
server.article_manager.article_list(sess, 'garbages')
article_dic = {'author':'serialx', 'title': 'polarbear', 'content': 'polarbear', 'method': 'web'}
