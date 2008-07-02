>>> import xmlrpclib

>>> s = xmlrpclib.Server("http://localhost:3939")
>>> s.login_manager.login('test', 'test', '143.248.234.145')
(True, '05a671c66aefea124cc08b76ea6d30bb')



"""
>>> s.article_manager.write_article("123","garbages",{
... "title":"123123123", "context":"11111111111"})
>>> [True, 1]

>>> s.article_manager.write_reply("123","garbages",{"context":"1111111"},1)
>>> [True, 'OK']

>>> s.article_manager.write_reply("123","garbages",{"context":"2222222"},1)
>>> [True, 'OK']

>>> s.article_manager.write_reply("123","garbages",{"context":"3333333"},1)
>>> [True, 'OK']

>>> s.article_manager.read("123","garbages",1)
[True,
 {'context': '11111111111',
  'reply': [{'context': '1111111'},
            {'context': '2222222'},
            {'context': '3333333'}],
  'title': '123123123'}]
"""
