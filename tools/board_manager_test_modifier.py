#-*- coding: utf-8 -*-

"""
TEST 코드들 중 Thrift object 를 직접 repr 하여 비교하는 코드가 상당히 있었는데 이 경우 Thrift 쪽에서 객체의 repr 타입을 바꾸는 순간 테스트가 모조리 와장창 깨지는 심각한 문제가 있었다. 이에 따라 객체를 일단 dictionary 화 한 뒤에 비교하는 전략을 취하는 것이 낫다고 판단하고 이미 repr 을 써서 되어 있는 테스트 코드를 읽어들여 repr  하는 부분을 전부 dictionary 화 한 것으로 교체하는 코드를 작성하게 되었다.

자세한 사용례는 본 changeset 의 diff 를 참조하도록 한다.
"""

def parse_data(data):

    data = data[7:-2]

    data = data.split(",")
    data = [x.strip().split("=") for x in data]
    
    data = ["'" + x[0] + "': " + x[1] for x in data]

    data = ", ".join(data)

    return "{" + data + "}"

def parse_repr(data):
    data = "self._to_dict"
    return data


def convert(data):
    import re
    result = re.search(r"(^.+?)(\"Board\(.+?\)\")(.+?)(repr)(\(.+\))(.+?$)", data, re.DOTALL)

    if result == None:
        # Parsing 하면 안되는 내용이 들어있다
        return data
    data = [result.group(x+1) for x in range(6)]

    for x in range(1, 6 + 1):
        #print x, data[x - 1]
        pass

    data[1] = parse_data(data[1])
    data[3] = parse_repr(data[3])

    return "".join(data)

f = open("board_manager_test.py", "r")
g = open("board_manager_test_new.py", "w")
for line in f:
    g.write(convert(line))
f.close()
g.close()
