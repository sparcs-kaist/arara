#!/usr/bin/env python
import os, sys

# ARAra Engine Specific Path Configuration
THRIFT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'gen-py'))
sys.path.append(THRIFT_PATH)
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(PROJECT_PATH)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "warara.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
