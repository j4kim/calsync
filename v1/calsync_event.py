import dateutil.parser
from pprint import pformat
from datetime import date, datetime, timedelta

class CalsyncEvent:
    def __init__(self):
        for attr in ["updated","google_id","exchange_id","changekey","is_new","is_updated"]:
            setattr(self, attr, None)

    def __repr__(self):
        return self.__class__.__name__ + '\n' + pformat(vars(self))

    def google_representation(self):
        g_dict = {}

        g_dict["iCalUID"] = self.id
        # if self.google_id:
        #     g_dict["id"] = self.google_id
        g_dict["summary"] = self.subject

        if self.updated:
            # je rajoute une microsecondes pour que google m'emmerde pas avec des formats de date incorrects
            self.updated += timedelta(microseconds=1)

            # updated : datetime -> yyyy-mm-ddThh:mm:ss.xxxZ
            g_dict["updated"] = self.updated.replace(tzinfo=None).isoformat() + 'Z'

        # start : date|datetime -> {"dateTime": "yyyy-mm-ddThh:mm:ss+01:00"}|{"date": "yyyy-mm-dd"}
        # end : date|datetime -> {"dateTime": "yyyy-mm-ddThh:mm:ss+01:00"}|{"date": "yyyy-mm-dd"}
        for param in ["start", "end"]:
            d = {}
            if self.is_all_day:
                d["date"] = getattr(self, param).isoformat()
            else:
                d["dateTime"] = getattr(self, param).isoformat()
            g_dict[param] = d

        return g_dict


class GoogleEvent(CalsyncEvent):
    def __init__(self, g_dict):
        CalsyncEvent.__init__(self)
        # for k,v in g_dict.items():
        #     setattr(self, k, v)

        # converti la str en datetime
        self.updated = dateutil.parser.parse(g_dict["updated"])
        for param in ["start", "end"]:
            # les events Google contiennent soit une date, soit une datetime pour les propriétés start et end
            if "dateTime" in g_dict[param]:
                # convertit la string en datetime
                dt = dateutil.parser.parse(g_dict[param]["dateTime"])
                setattr(self, param, dt)
                self.is_all_day = False
            elif "date" in g_dict[param]:
                # convertit la string en datetime, puis ne récupère que la date
                d = dateutil.parser.parse(g_dict[param]["date"]).date()
                setattr(self, param, d)
                self.is_all_day = True

        self.subject = g_dict["summary"]
        self.id = g_dict["iCalUID"]
        self.google_id = g_dict["id"]

class ExchangeEvent(CalsyncEvent):
    pass

class IcsEvent(CalsyncEvent):
    pass