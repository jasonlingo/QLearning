class Aclass(object):


    def __init__(self):
        self.k = "A"
        print "A init"


    def __eq__(self, other):
        return True

    def do(self):
        print self.k + "doing"


class Bclass(Aclass):

    def __init__(self):
        Aclass.__init__(self)
        self.k = "B"



aa = Bclass()
cc = Bclass()

print aa == cc