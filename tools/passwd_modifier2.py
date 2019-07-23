# this is made by richking
# for temp usage

import sys
import os
sys.path.append("/home/ara/ara/gen-py")
sys.path.append("/home/ara/ara/")
from arara import arara_engine
from arara import model
model.init_database()
a = arara_engine.ARAraEngine()

passwd = raw_input("password(SYSOP) : ")

session = a.login_manager.login('SYSOP', passwd, '127.0.0.1')

# wrong password???
print session

username = raw_input("username : ")
passwd = raw_input("new passwd : ")
from arara_thrift.ttypes import *
a.member_manager.modify_password_sysop(session, UserPasswordInfo(username=username, new_password=passwd))

