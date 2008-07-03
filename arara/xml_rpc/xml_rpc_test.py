import xmlrpclib

s = xmlrpclib.Server('http://localhost:4949')
test= s.login_manager.login('test', 'test', '143.248.234.145')

print s.article_manager.write_article(test[1], 'garbages', {'title':'123', 'cont':'234'})
print s.article_manager.write_reply(test[1], 'garbages', {'context':'222'}, 1)
print s.article_manager.read(test[1], 'garbages', 1)

