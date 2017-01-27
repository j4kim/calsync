from pprint import pformat

class CalsyncEvent:
    """Abstract class representing all events manipulated with calsync"""

    def __init__(self):
        """Initialise attributes, set them to value None"""
        for attr in ["updated","google_id","exchange_id","changekey","is_new","is_updated"]:
            setattr(self, attr, None)

    def __repr__(self):
        return self.__class__.__name__ + '\n' + pformat(vars(self))
