all:
	thrift -v -gen py -gen rb -gen java -gen cpp thrift/arara.thrift
clean:
	rm -r gen-*/
