import os
import sys

THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gen-py'))
ARARA_PATH  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(THRIFT_PATH)
sys.path.append(ARARA_PATH)

os.environ['DJANGO_SETTINGS_MODULE'] = 'warara.settings'

from warara.warara_middleware import get_server
from arara_thrift.ttypes import *
