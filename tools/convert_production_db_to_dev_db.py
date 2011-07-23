#-*- coding: utf-8 -*-
'''
Convert Production DB into Dev-purpose DB
실제 서비스의 DB 에서 치명적인 정보를 제거한 개발용 DB 를 생성한다.

주의: etc/arara_settings.py 에 지정된 DB 를 질의 없이 바로 편집한다.
      절.대.로. 서비스 머신에서 함부로 사용하지 말 것.

일어나는 변화들

1) 모든 사용자의 username 이 임의의 알파벳 3글자 + 숫자로 변경된다.
   nickname 과 e-mail 인증 정보 또한 동일하게 변경된다.
   (단, SYSOP 계정의 username 만은 여전히 SYSOP 으로 유지된다.)
   모든 사용자의 비밀번호가 1234 로 설정된다.
   그리고 사용자의 Signature 와 Introduction 은 전부 알파벳 x 로 채워진다.

2) 모든 사용자가 주고받은 모든 message 의 본문의 모든 글자를 알파벳 x 로 채운다.

3) 작성된 모든 글의 작성자 Nickname 정보 (글 쓸 때 보존됨) 를 글 번호로 바꾼다.
'''
# TODO: Clear private information more and more

# TODO: 파라메터로 편집할 정보를 지정할 수 있게 한다.
# TODO: 좀더 Interactive 하게 사용할 수 있도록 한다.

import os
import sys

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gen-py'))
ARARA_PATH  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(THRIFT_PATH)
sys.path.append(ARARA_PATH)

import random

from arara import model
from arara.util import smart_unicode

def inttostr(n):
    s = "%d" % n
    s = "0" * (6 - len(s)) + s
    return s


class DatabaseConverter(object):
    def __init__(self):
        model.init_database()

    def modify_user_info(self):
        '''
        User 객체들의 개인정보를 제거한다.
        또한 Username 을 마구 섞어준다.
        '''
        s = model.Session()
        query = s.query(model.User)

        length = query.count()
        print "Modifying", length, "users ..."

        new_username_list = range(length)
        random.shuffle(new_username_list)

        prefix = "".join(random.sample("abcdefghijklmnopqrstuvwxyz", 3))

        print "Username Prefix:", prefix

        for idx, user in enumerate(query):
            user.username = prefix + inttostr(new_username_list[idx])
            user.nickname = user.username
            user.email = smart_unicode(inttostr(user.id) + "@example.com")
            user.signature = u"x" * len(user.signature)
            user.self_introduction = u"x" * len(user.self_introduction)
            user.last_login_ip = u"127.0.0.1"
            user.set_password("1234")

        print "commit begin"
        s.commit()

        # SYSOP 사용자 (1번 사용자) 의 개인정보는 원상복귀시킨다
        sysop = s.query(model.User).filter_by(id=1).one()
        sysop.username = "SYSOP"
        sysop.nickname = "SYSOP"
        s.commit()

        s.close()
        print "commit done"

    def modify_message_info(self):
        """
        사용자들이 주고받은 message 내용을 전부 숨긴다
        """
        s = model.Session()
        query = s.query(model.Message)

        length = query.count()
        print "Modifying", length, "messages ..."

        for idx, message in enumerate(query):
            message.message = u"x" * len(message.message)

        print "commit begin"
        s.commit()
        print "commit done"

    def modify_article_info(self):
        """
        Article 테이블에 사용자의 Nickname 이 남은 것을 지운다.
        """
        s = model.Session()
        query = s.query(model.Article)

        length = query.count()
        print "Modifying", length, "articles ..."

        for idx in xrange(1, length + 1):
            cond = model.articles_table.c.id == idx
            s.execute(model.articles_table.update().values(author_nickname=inttostr(idx)).where(cond))
            if idx % (length / 100) == 0:
                print idx

        print "commit begin"
        s.commit()
        print "commit done"


def main():
    conv = DatabaseConverter()
    conv.modify_user_info()
    conv.modify_message_info()
    conv.modify_article_info()

if __name__ == "__main__":
    main()
