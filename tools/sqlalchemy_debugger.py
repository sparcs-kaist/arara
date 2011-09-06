#-*- coding: utf-8 -*-
'''
SQLAlchemy 의 query 를 직접 들여다볼 수 있도록 해 준다.

참고
====

http://stackoverflow.com/questions/4617291/how-do-i-get-a-raw-compiled-sql-query-from-a-sqlalchemy-expression
'''
from MySQLdb.converters import conversions, escape
from sqlalchemy.sql import compiler


def compile_query(query):
    '''
    주어진 SQLAlchemy Query 풀버전을 문자열로 돌려준다.

    >>> query = model.Session().query(model.Board)
    >>> print compile_query(query)
    u'SELECT boards.id, boards.category_id, boards.board_name, boards.board_alias, boards.board_description, boards.deleted, boards.read_only, boards.hide, boards."order", boards.type, boards.to_read_level, boards.to_write_level \nFROM boards'

    @type  query: sqlalchemy.orm.query.Query
    @param query: 들여다볼 쿼리 객체
    @rtype: str
    @return: 쿼리문 본문
    '''
    dialect = query.session.bind.dialect
    statement = query.statement
    comp = compiler.SQLCompiler(dialect, statement)
    comp.compile()
    enc = dialect.encoding
    params = []
    for key in comp.positiontup:
        value = comp.params[key]
        if isinstance(value, unicode):
            value = value.encode(enc)
        params.append(escape(value, conversions))
    return (comp.string.encode(enc) % tuple(params)).decode(enc)
