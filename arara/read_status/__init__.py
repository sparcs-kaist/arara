# -*- coding: utf-8 -*-
from libs import intlist_to_string, smart_unicode, string_to_intlist

class ReadStatus(object):
    def __init__(self, default='N'):
        self.default = default
        self.data = [(0, default)]

    def to_string(self):
        '''
        ReadStatus 객체로부터 2개의 문자열을 뽑아낸다.
        '''
        number_list = intlist_to_string([x[0] for x in self.data])
        marker_list = "".join((x[1] for x in self.data))
        return number_list, marker_list

    @classmethod
    def from_string(cl, number_string, marker_string):
        '''
        2개의 문자열로부터 ReadStatus 객체를 만들어낸다.

        @type  number_string: string
        @param number_string: util.intlist_to_string 으로 문자열화한 list<int>
        @type  marker_string: string
        @param marker_string: len(number_string == len(marker_string) 인 문자열
        @rtype: ReadStatus
        @return: 주어진 문자열을 통해 만든 ReadStatus 객체
        '''
        result = cl()
        number_list = string_to_intlist(number_string)
        result.data = [(x, marker_string[idx]) for idx, x in enumerate(number_list)]
        return result

    def _find(self, n):
        '''적당한 터플을 찾는다'''
        low = 0
        high = len(self.data) - 1
        while True:
            middle = (high - low) / 2 + low
            assert low <= middle <= high
            if self.data[middle][0] <= n:
                try:
                    if n < self.data[middle+1][0]:
                        return middle
                except IndexError:
                    return middle
            if self.data[middle][0] <= n:
                low = middle + 1
            else:
                high = middle - 1

    def get(self, n):
        idx = self._find(n)
        return self.data[idx][1]

    def get_range(self, range_list):
        ret = []
        for i in range_list:
            ret.append(self.get(i))
        return ret

    def set_range(self, range_list, value):
        for i in range_list:
            self.set(i, value)
        return True

    def _merge_right(self, idx):
        if self.data[idx][1] == self.data[idx + 1][1]:
            del self.data[idx + 1]

    def _merge_left(self, idx):
        self._merge_right(idx - 1)

    def _merge(self, idx):
        #print idx
        if idx == 0:
            self._merge_right(idx)
        elif idx == len(self.data) - 1:
            self._merge_left(idx)
        else:
            self._merge_right(idx)
            self._merge_left(idx)

    def set(self, n, value):
        found_idx = self._find(n)
        found_lower_bound = self.data[found_idx][0]
        found_value = self.data[found_idx][1]
        if found_value == value: return

        # 맨 앞일경우
        if n == 0:
            self.data[0] = (0, value)
            if len(self.data) == 1:
                self.data.append((1, self.default))
                self._merge(0)
            elif self.data[1][0] != 1:
                self.data.insert(1, (1, self.default))
                self._merge(1)
            return

        if found_lower_bound == n:
            self.data[found_idx] = (n, value)
            if len(self.data) == found_idx + 1:
                self.data.append((n + 1, self.default))
            elif self.data[found_idx + 1][0] != n + 1:
                assert self.data[found_idx + 1][0] != n
                self.data.insert(found_idx + 1, (n + 1, self.default))
                self._merge(found_idx)
            self._merge(found_idx - 1)
            return

        # 찾은 터플의 값이 셋팅 하려는 값과 다르므로 새로 맹근다.
        self.data.insert(found_idx + 1, (n, value))
        if len(self.data) == found_idx + 2:
            self.data.append((n + 1, self.default))
        elif self.data[found_idx + 2][0] != n + 1:
            self.data.insert(found_idx + 2, (n+1, self.default))
        self._merge(found_idx)
        self._merge(found_idx + 1)

    def __repr__(self):
        printed_str = ""
        for item in self.data:
            printed_str += str(item)
        return printed_str

