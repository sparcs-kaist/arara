#/usr/bin/python2.5

import arara.tests
import unittest

if __name__ == '__main__':
    try: 
        import testoob 
        testoob.main(defaultTest="arara.tests.suite") 
    except ImportError: 
        unittest.TextTestRunner().run(arara.tests.suite()) 
