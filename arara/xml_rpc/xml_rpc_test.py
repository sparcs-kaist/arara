import xmlrpclib

s = xmlrpclib.Server('http://localhost:3939')
print s.login_manager.login('test', 'test', '143.248.234.145')

print s.article_manager.write_article('123', 'garbages', {'title':'123', 'cont':'234'})
print s.article_manager.write_reply('123', 'garbages', {'context':'222'}, 1)
print s.article_manager.read('123', 'garbages', 1)

