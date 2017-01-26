from pprint import pformat

class CalsyncEvent:
    def __init__(self):
        for attr in ["updated","google_id","exchange_id","api_id","changekey","is_new","is_updated"]:
            setattr(self, attr, None)

    def __repr__(self):
        return self.__class__.__name__ + '\n' + pformat(vars(self))
