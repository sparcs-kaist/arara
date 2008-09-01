#!/usr/bin/python
import os
import gettext
LOCALE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
t = gettext.translation('ara', LOCALE_PATH)
_ = t.ugettext
