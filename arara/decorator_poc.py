class PrintYes(object):
    enabled = True
    def __init__(self, function):
        self.function = function
    def __call__(self, *args):
        if self.enabled:
            print 'yes'
        return self.function(*args)

def print_yes(function):
    return PrintYes(function)

@print_yes
def plus(a, b):
    return a + b

class C:
    @print_yes
    def plus(self, a, b):
        return a + b

print plus(1, 1)
PrintYes.enabled = False
print plus(1, 1)
PrintYes.enabled = True

c = C()
print c.plus(2, 2)
PrintYes.enabled = False
print c.plus(2, 2)
PrintYes.enabled = True
