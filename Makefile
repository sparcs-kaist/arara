# 현재 python 만 사용되고 있으므로 다른 건 필요없다.
all:
	thrift -v -gen py thrift/arara.thrift
clean:
	rm -r gen-*/
