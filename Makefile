all:
	thrift -v -gen py:new_style=true -gen rb -gen java -gen cpp thrift/arara.thrift
clean:
	rm -r gen-*/
