
class Job:

    def __init__(self, **kwargs):
        print("Job(self, kwargs)")
        for k, v in kwargs.items():
            print("  k '%s' -> v '%s'" % (k,v))

    def run(self, **kwargs):
        print("Job.run(self, kwargs)")
