
# for generating unique car id
# carID = 0





class UniqueID():
    """
    Plus one to carID and return it to make the id for each car unique.
    :return: car id
    """
    carID = 0

    @classmethod
    def getID(cls):
        cls.carID += 1
        return cls.carID

