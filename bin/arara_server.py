#!/usr/bin/python
from SimpleXMLRPCServer import SimpleXMLRPCServer
import os
import sys
import optparse

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(PROJECT_PATH)

import arara

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port=", dest="port", default=8000, type="int",
                      help="The port to bind")
    options, args = parser.parse_args()
    print "Opening ARAra XMLRPC middleware on port", options.port, "..."

    server = SimpleXMLRPCServer(("", options.port))
    server.register_introspection_functions()

    server.register_instance(arara.get_namespace(), allow_dotted_names=True)

    server.serve_forever()

# vim: set et ts=8 sw=4 sts=4
