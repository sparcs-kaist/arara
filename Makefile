# 현재 python 만 사용되고 있으므로 다른 건 필요없다.
all:
	thrift -v -gen py thrift/arara.thrift
clean:
	rm -f `find * -name *.pyc`
pep8:
	tools/run_pep8.sh `hg st | egrep "^[MA].+.py$$" | awk '{print $$2}'`
pyflakes:
	tools/run_pyflakes.sh `hg st | egrep "^[MA].+.py$$" | awk '{print $$2}'`
pylint:
	tools/run_pylint.sh `hg st | egrep "^[MA].+.py$$" | awk '{print $$2}'`
check: pep8 pyflakes pylint
