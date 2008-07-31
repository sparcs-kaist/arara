#!/usr/bin/python

import xmlrpclib
server = xmlrpclib.Server('http://localhost:8000')
server.article_manager.article_list(u'00', u'garbages')
server.article_manager.article_list(u'000123', u'garbages')
# mikkang
user_reg_dic = {'username':u'mikkang', 'password':u'mikkang', 'nickname':u'mikkang', 'email':u'mikkang', 'signature':u'mikkang', 'self_introduction':u'mikkang', 'default_language':u'english' }
print user_reg_dic
_, reg_key = server.member_manager.register(user_reg_dic)
server.member_manager.confirm(u'mikkang', unicode(reg_key))
ret, sess = server.login_manager.login(u'mikkang', u'mikkang', u'12')

# breadfish
user_reg_dic = {'username':u'breadfish', 'password':u'breadfish', 'nickname':u'breadfish', 'email':u'breadfish', 'signature':u'breadfish', 'self_introduction':u'breadfish', 'default_language':u'english' }
_, reg_key = server.member_manager.register(user_reg_dic)
server.member_manager.confirm(u'breadfish', unicode(reg_key))
ret_breadfish, sess_breadfish = server.login_manager.login(u'breadfish', u'breadfish', u'127.0.0.1')

# jacob
user_reg_dic = {'username':u'jacob', 'password':u'jacob', 'nickname':u'jacob', 'email':u'jacob', 'signature':u'jacob', 'self_introduction':u'jacob', 'default_language':u'english' }
_, reg_key = server.member_manager.register(user_reg_dic)
server.member_manager.confirm(u'jacob', unicode(reg_key))
ret_jacob, sess_jacob = server.login_manager.login(u'jacob', u'jacob', u'127.0.0.1')

ret, sess_sysop = server.login_manager.login(u'SYSOP', u'SYSOP', u'123.123.123.123')
server.board_manager.add_board(sess_sysop, u'garbages', u'Garbages board')

article_dic = {'title': u'serialx is...', 'content': u'polarbear', 'method': u'web'}
server.article_manager.write_article(sess, u'garbages', article_dic)
article_dic = {'title': u'polarbear', 'content': u'polarbear', 'method': u'web'}
server.article_manager.write_article(sess, u'garbages', article_dic)
server.article_manager.article_list(sess, u'garbages')
article_dic = {'title': u'polarbear', u'content': u'polarbear', 'method': u'web'}
for i in range(900, 930):
    server.messaging_manager.send_message(sess, u'breadfish', unicode(''.join([str(i)]*10)))

server.blacklist_manager.add(sess, u'breadfish')
