from datetime import timezone, timedelta

import dateutil.parser

from calsync_event import CalsyncEvent


class GoogleEvent(CalsyncEvent):
    """Implementation of CalsyncEvent that reads a google representation and convert it to calsync"""

    def __init__(self, g_dict):
        """Initialize a CalsyncEvent from a google dictionnary retrieved by the Google API"""

        CalsyncEvent.__init__(self)

        self.id = g_dict["iCalUID"]
        self.subject = g_dict["summary"]
        self.google_id = g_dict["id"]

        # convert the string in a datetime object
        self.updated = dateutil.parser.parse(g_dict["updated"])
        for param in ["start", "end"]:
            # Google Calendar's events can contain either a date
            # or a datetime object for the start and end properties
            # if it's a date, that means the event is all day
            if "dateTime" in g_dict[param]:
                dt = dateutil.parser.parse(g_dict[param]["dateTime"])
                setattr(self, param, dt)
                self.is_all_day = False
            elif "date" in g_dict[param]:
                # convert the string in a datetime object, then gets only the date
                d = dateutil.parser.parse(g_dict[param]["date"]).date()
                setattr(self, param, d)
                self.is_all_day = True


def to_google(c_event):
    """Convert a CalsyncEvent to a google-API-compatible dictionnary"""
    g_dict = {}

    g_dict["iCalUID"] = c_event.id
    # if self.google_id:
    #     g_dict["id"] = self.google_id
    g_dict["summary"] = c_event.subject

    if c_event.updated:
        # je rajoute une microsecondes pour que google m'emmerde pas avec des formats de date incorrects
        # avec python 3.6, la méthode isoformat prend un argument timespec, ce qui aurait facilité les choses
        # self.updated.replace(tzinfo=None).isoformat(timespec='microseconds') + 'Z'
        # todo: faire le zero-padding à la main
        c_event.updated += timedelta(microseconds=1)

        # updated : datetime -> yyyy-mm-ddThh:mm:ss.xxxZ
        g_dict["updated"] = c_event.updated.replace(tzinfo=None).isoformat() + 'Z'

    # start : date|datetime -> {"dateTime": "yyyy-mm-ddThh:mm:ss+01:00"}|{"date": "yyyy-mm-dd"}
    # end : date|datetime -> {"dateTime": "yyyy-mm-ddThh:mm:ss+01:00"}|{"date": "yyyy-mm-dd"}
    for param in ["start", "end"]:
        d = {}
        if c_event.is_all_day:
            d["date"] = getattr(c_event, param).isoformat()
        else:
            dt = getattr(c_event, param)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            d["dateTime"] = dt.isoformat()
        g_dict[param] = d

    return g_dict