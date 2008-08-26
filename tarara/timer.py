#!/usr/bin/python
import time
import threading

class Timer(threading.Thread):
    def __init__(self, interval, function, args=[]):
        threading.Thread.__init__(self)
        self.interval = interval
        self.state = False
        self.function = function

    def run(self):
        self.state = True
        while self.state:
            time.sleep(self.interval)
            if self.function != None:
                    self.function()

    def cancel(self):
        self.state = False                   

# vim: set et ts=8 sw=4 sts=4:

