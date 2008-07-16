#!/usr/bin/python
# coding: utf-8

'''
List view 관련 모듈.
이 모듈에서 필요한 것:

* rowitem 클래스. widget 모듈의 FieldRow를 상속받은 형태를 사용한다.
* 키:값으로 이루어져 있는 데이터의 목록. 이 데이터를 표시한다.
'''

import widget
import urwid


def make_widget(data, rowitem):
    '''
    dictionary 형태로 된 입력 데이터를 rowitem으로 가공하는 함수.
    rowitem 클래스는 widget.FieldRow의 하위 클래스이다.

    rowitem 클래스의 예제:

    class RowItem(widget.FieldRow):
        fields = [
            ('number', 5, 'right'),
            ('id', 8, 'left'),
            ('name', 10, 'left'),
            ('date', 5, 'right'),
            ('subject', 0, 'left'),
        ]

    @type data: dict
    @param data: 각 열에 해당하는 데이터를 담고 있는 dictionary.
    @type rowitem: widget.FieldRow
    @param rowitem: 열 정보를 담고 있는 FieldRow의 자식 클래스.
    @rtype: widget.MarkerSelect
    @return: 위젯 rowitem.
    '''
    return widget.MarkedItem('>', rowitem(data))

def make_header(data, rowitem):
    '''
    헤더 데이터를 받아서 rowitem을 만들어 주는 함수.

    data의 예제: {'number': u'번호', 'id': u'글쓴이', 'name': u'이름', 'date': u'날짜', 'subject': u'제목'}

    @type data: dict
    @param data: 헤더 데이터
    @type rowitem: widget.FieldRow
    @param rowitem: 열 정보를 담고 있는 FieldRow의 자식 클래스.
    @rtype: urwid.AttrWrap
    @return: 헤더 rowitem.
    '''
    return urwid.AttrWrap(make_widget(data, rowitem), 'reversed')

def get_view(datalist, header, rowitem):
    '''
    헤더와 데이터를 합쳐서 완성된 리스트 뷰를 만들어 주는 함수.

    datalist의 예제: [{'number': '1', 'id': '2', 'name': 'peremen', 'date': 'today', 'subject': 'good article'}]

    @type datalist: list
    @param data: 각 열에 해당하는 데이터를 담고 있는 dictionary의 목록.
    @type rowitem: widget.FieldRow
    @param rowitem: 열 정보를 담고 있는 FieldRow의 자식 클래스.
    @rtype: urwid.Frame
    @return: 리스트 뷰 프레임.
    '''
    walker = urwid.SimpleListWalker([make_widget(datum, rowitem) for datum in datalist])

    body = urwid.ListBox(walker)
    header = make_header(header, rowitem)
    return urwid.Frame(body, header)

# vim: set et ts=8 sw=4 sts=4:

