all:
	thrift -gen py:new_style=true -gen rb -gen java -gen cpp arara.thrift
clean:
	rm -r gen-*/
