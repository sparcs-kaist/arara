#!/usr/bin/python

import xmlrpclib
server = xmlrpclib.Server('http://localhost:8000')
server.article_manager.article_list('00', 'garbages')
server.article_manager.article_list('000123', 'garbages')
user_reg_dic = {'id':'mikkang', 'password':'mikkang', 'nickname':'mikkang', 'email':'mikkang', 'sig':'mikkang', 'self_introduce':'mikkang', 'default_language':'english' }
_, reg_key = server.member_manager.register(user_reg_dic)
server.member_manager.confirm('mikkang', reg_key)
ret, sess = server.login_manager.login('mikkang', 'mikkang', '12')
user_reg_dic = {'id':'breadfish', 'password':'breadfish', 'nickname':'breadfish', 'email':'breadfish', 'sig':'breadfish', 'self_introduce':'breadfish', 'default_language':'english' }
_, reg_key = server.member_manager.register(user_reg_dic)
server.member_manager.confirm('breadfish', reg_key)
ret_breadfish, sess_breadfish = server.login_manager.login('breadfish', 'breadfish', '127.0.0.1')
article_dic = {'author':'serialx', 'title': 'serialx is...', 'content': 'polarbear', 'method': 'web'}
server.article_manager.write_article(sess, 'garbages', article_dic)
article_dic = {'author':'serialx', 'title': 'polarbear', 'content': 'polarbear', 'method': 'web'}
server.article_manager.write_article(sess, 'garbages', article_dic)
server.article_manager.article_list(sess, 'garbages')
article_dic = {'author':'serialx', 'title': 'polarbear', 'content': 'polarbear', 'method': 'web'}
for i in range(900, 1000):
    server.messaging_manager.send_message(sess, 'breadfish', ''.join([str(i)]*20))
