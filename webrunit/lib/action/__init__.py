
class Action:

    def __init__(self, **kwargs):
        print("Action(self, kwargs)")
        for k, v in kwargs.items():
            print("  k '%s' -> v '%s'" % (k,v))

    def run(self, **kwargs):
        print("Action.run(self, kwargs)")
