# -*- coding: utf-8

#KAIST SSO authentication -- Kidnapped from OTL

### Usage ###########################################################
#                                                                   #
# Method    : authenticate                                          #
# Variable  : username, password                                    #
# Return    : If username & password are correct  -> kuser_info     #
#             Else                                -> None           #
#                                                                   #
#####################################################################

import urllib, urllib2
import base64
import re

_rx_name_val = re.compile(r"name=([^ ]*) value='([^']*)'")

class KAISTSSOBackend:
    
    def authenticate(self, username=None, password=None):

        request_info = [
            ('isenc', 't'),
            ('b001', base64.b64encode(username)),
            ('b002', base64.b64encode(password)),
            ('b003', 'givenname'),
            ('b003', 'sn'),
            ('b003', 'uid'),
            ('b003', 'mail'),
            ('b003', 'ku_where'),
            ('b003', 'ku_departmentname'),
            ('b003', 'ku_socialName'),
            ('b003', 'ku_regno1'),
            #('b003', 'ku_regno2'), # We don't need the civil registration number.
            ('b003', 'ku_dutyName'),
            ('b003', 'ku_dutyCode'),
            ('b003', 'ku_socialName'),
            ('b003', 'ku_socialcode'),
            ('b003', 'ku_titleCode'),
            ('b003', 'ku_status'),
        ]

        request = urllib2.Request('http://addr.kaist.ac.kr/auth/authenticator')
        username_enc = base64.b64encode(username)
        password_enc = base64.b64encode(password)

        # TODO: register ara.kaist.ac.kr to IT service department.
        request.add_header('Referer', 'http://moodle.kaist.ac.kr')
        request.add_data(urllib.urlencode(request_info))

        try:
            ret = urllib2.urlopen(request).read()
            ret = urllib.unquote_plus(ret)
        except urllib2.HTTPError: # Login failed
            return None
        
        matches = _rx_name_val.findall(ret);
        kuser_info = dict(map(lambda item: (item[0], item[1].decode('cp949')), matches))
        kuser_info['student_id'] = kuser_info['ku_status'].split('=')[0]
        if ';:' in kuser_info['ku_departmentname']: # users merged from ICU
            kuser_info['department'] = kuser_info['ku_departmentname'].split('=')[1].split(';')[0]
        else: # original KAIST users
            kuser_info['department'] = kuser_info['ku_departmentname'].split('=')[1][:-1]

        return kuser_info;


# For Testing
if __name__ == '__main__':
    import getpass
    b = KAISTSSOBackend()
    username = raw_input('Username: ')
    password = getpass.getpass()
    user_info = b.authenticate(username, password)
    if user_info == None:
        print "Login Failed!"
    else:
        print "Hello " + user_info['student_id']
        print "Login Success"
