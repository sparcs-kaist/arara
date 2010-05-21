#-*- coding: utf-8 -*-
# NeoARA -> ARAra Migrator
# Author : Sung Mo Koo (breadfish@sparcs.kaist.ac.kr)
# 네오아라 / 웹아라에서 아라라 엔진으로 사용자 정보를 이전하는 툴.
import os
import MySQLdb
import arara
import md5 as hashlib


def mig_user():
    server = arara.get_server()
    user = {}
    error = ''
    for root, dirs, files in os.walk("."): #read userinfo from files

        root_split = root.split("/")
        if len(root_split) == 4:
            user['id'] = root_split[-1]

            if 'lastlogin' in files: #lastlogin
                user['lastlogin'] = file(root + '/lastlogin').read()
            if 'signature' in files: #signature
                user['signature'] = file(root + '/signature').read()
            if 'profile' in files:
                user['email_address'] = file(root + '/profile').read().replace('MAIL=', '')
            if 'mail' in dirs: #mail
                user['email'] = {}
                user['email']['content'] = ''
                for mail in os.listdir(root + '/mail'):
                    isheader = 1 #the flag whther the line is header or content
                    for line in file('/'.join([root, 'mail', mail])):
                        if line == '\n':
                            isheader = 0
                        if isheader:
                            user['email'][line.split(': ')[0]] = line.split(': ')[-1]
                        else:
                            user['email']['content'] += line
    file('error', 'w').write(error)

    #read userinfo from mysql
    db = MySQLdb.connect(host='mir.sparcs.org', user='breadfish', passwd='q1q1q1', db='webara2g')
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('set names utf8')
    cursor.execute('SELECT * FROM users LIMIT 100,10')
    rec = cursor.fetchall()
    cursor.execute('show tables')
    tables  = cursor.fetchall()

def mig_article():
    server = arara.get_server()
    article_dir = "./articles"
    db = MySQLdb.connect(host='mir.sparcs.org', user='breadfish', passwd='q1q1q1', db='webara2g')
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('set names utf8')
    
    boards = os.listdir(article_dir)
    for board in boards:
        if not os.path.isdir(article_dir + '/' + board): #if the directory of the board does not exist
            continue
        suc, board_list = server.board_manager.get_board_list()
        if not board in [exist_board['board_name'] for exist_board in board_list]: #if the board is not exist
            suc, sess = server.login_manager.login('SYSOP', 'SYSOP', '')
            suc, mes = server.board_manager.add_board(sess, board, 'add description later')
            suc, mes = server.login_manager.logout(sess)
        board_table = 'webara_' + hashlib.md5('kaist.bbs.ara.' + board).hexdigest()
        cursor.execute('select max(depth) from ' + board_table)
        max_depth = cursor.fetchall()[0]['max(depth)']
        max_depth = int(max_depth)
        for depth in range(max_depth+1):
            cursor.execute('SELECT * FROM ' + board_table + ' WHERE depth=' + str(depth) + ' LIMIT 5000,100')
            #cursor.execute('SELECT * FROM ' + board_table + ' WHERE depth=' + str(depth))
            article_results = cursor.fetchall()
            for article_result in article_results:
                article = {}
                article['content'] = ''
                article_file = '/'.join([article_dir, board, str(article_result['msgnb'])])
                if not os.path.isfile(article_file):
                    continue
                iscontent = 0 #the flag whther the line is header or content
                for line in file(article_file):
                    if iscontent:
                        article['content'] += line
                    if line == '\n':
                        iscontent = 1
                if article_result['parent'] == 0:
                    pass #article write function need
                else:
                    parent = int(article_result['parent'])
                    pass #reply write function need

def mig_read_status():
    server = arara.get_server()
    user = {}
    error = ''
    for root, dirs, files in os.walk("."): #read userinfo from files

        root_split = root.split("/")
        if len(root_split) == 4:
            user['id'] = root_split[-1]

            for file_name in files:
                #if file_name.count('newsrc') and not file_name.count('20060809') and not file_name.count('bak') and not file_name.count('webara'):
                if file_name.count('newsrc'):
                    user['read_status'] = {}
                    for line in file('/'.join([root, file_name])):
                        line = line.replace('\n', '')
                        line = line.replace(' ', '')
                        board_name = line.split(':')[0].split('.')[-1]
                        user['read_status'][board_name] = []
                        for article_no in line.split(':')[-1].split(','):
                            if article_no == '':
                                continue
                            elif article_no.count('-'):
                                try:
                                    if int(article_no.split('-')[-1]) > 200000:
                                        error += '/'.join([root, file_name, board_name, article_no]) + '\n'
                                        continue
                                    user['read_status'][board_name] += range(int(article_no.split('-')[0]), int(article_no.split('-')[-1]))
                                except ValueError:
                                    if article_no.split('-')[0] == '' or article_no.split('-')[-1] == '':
                                        article_no = article_no.replace('-', '')
                                        user['read_status'][board_name].append(int(article_no))
                                    else:
                                        error += '/'.join([root, file_name, board_name, article_no]) + '\n'
                            else:
                                if article_no.isdigit():
                                    user['read_status'][board_name].append(int(article_no))
                                else:
                                    error += '/'.join([root, file_name, board_name, article_no]) + '\n'

    file('error', 'w').write(error)

mig_article()
mig_user()
mig_read_status()
