#!/usr/bin/python
# XML-RPC 서버 개발중에 잠깐 쓰였던 파일.
import xmlrpclib

s = xmlrpclib.Server('http://localhost:4949')
test= s.login_manager.login('test', 'test', '143.248.234.145')

print s.article_manager.write_article(test[1], 'garbages', {'title':'123', 'cont':'234'})
print s.article_manager.write_reply(test[1], 'garbages', {'context':'222'}, 1)
print s.article_manager.read(test[1], 'garbages', 1)


# vim: set et ts=8 sw=4 sts=4
