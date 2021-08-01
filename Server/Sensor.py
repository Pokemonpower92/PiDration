''' Sensor class '''

class Sensor:

    def __init__(self, **kwargs):
        self.name    = kwargs.get("name")
        self.address = kwargs.get("address")
        self.id      = kwargs.get("id")
        self.data    = kwargs.get("data", [])