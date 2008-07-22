#!/usr/bin/python

import xmlrpclib
server = xmlrpclib.Server('http://localhost:8000')
server.article_manager.article_list('00', 'garbages')
server.article_manager.article_list('000123', 'garbages')
# mikkang
user_reg_dic = {'username':'mikkang', 'password':'mikkang', 'nickname':'mikkang', 'email':'mikkang', 'signature':'mikkang', 'self_introduction':'mikkang', 'default_language':'english' }
_, reg_key = server.member_manager.register(user_reg_dic)
server.member_manager.confirm('mikkang', reg_key)
ret, sess = server.login_manager.login('mikkang', 'mikkang', '12')

# breadfish
user_reg_dic = {'username':'breadfish', 'password':'breadfish', 'nickname':'breadfish', 'email':'breadfish', 'signature':'breadfish', 'self_introduction':'breadfish', 'default_language':'english' }
_, reg_key = server.member_manager.register(user_reg_dic)
server.member_manager.confirm('breadfish', reg_key)
ret_breadfish, sess_breadfish = server.login_manager.login('breadfish', 'breadfish', '127.0.0.1')

# jacob
user_reg_dic = {'username':'jacob', 'password':'jacob', 'nickname':'jacob', 'email':'jacob', 'signature':'jacob', 'self_introduction':'jacob', 'default_language':'english' }
_, reg_key = server.member_manager.register(user_reg_dic)
server.member_manager.confirm('jacob', reg_key)
ret_jacob, sess_jacob = server.login_manager.login('jacob', 'jacob', '127.0.0.1')


article_dic = {'author':'serialx', 'title': 'serialx is...', 'content': 'polarbear', 'method': 'web'}
server.article_manager.write_article(sess, 'garbages', article_dic)
article_dic = {'author':'serialx', 'title': 'polarbear', 'content': 'polarbear', 'method': 'web'}
server.article_manager.write_article(sess, 'garbages', article_dic)
server.article_manager.article_list(sess, 'garbages')
article_dic = {'author':'serialx', 'title': 'polarbear', 'content': 'polarbear', 'method': 'web'}
for i in range(900, 930):
    server.messaging_manager.send_message(sess, 'breadfish', ''.join([str(i)]*10))

server.blacklist_manager.add(sess, 'breadfish')
