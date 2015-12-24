

class Super(object):

    def __init__(self):
        self.a = 100



class Subclass(Super):

    def __init__(self):
        # Super.__init__(self)
        Super.__init__(self)
        self.b = 200



x = Subclass()
print x.a
print x.b