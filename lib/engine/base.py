
class Engine:

    def __init__(self, **kwargs):
        print("Engine(self, kwargs)")
        for k, v in kwargs.items():
            print("  k '%s' -> v '%s'" % (k,v))
            if k == 'type':
                if 'v' == 'local':
                    return LocalEngine(self, kwargs)

    def run(self, **kwargs):
        print("Engine.run(self, kwargs)")
