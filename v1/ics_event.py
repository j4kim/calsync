from datetime import date, datetime, timezone

from icalendar import vDDDTypes, Event

from calsync_event import CalsyncEvent


class IcsEvent(CalsyncEvent):
    def __init__(self, component):
        CalsyncEvent.__init__(self)

        self.subject = component.get("summary") + ""  # avoid vText()

        for param in ["start","end"]:
            d = component.get('dt'+param) # on ne sait pas si date ou datetime
            ddd = vDDDTypes.from_ical(d) # retourne soit un objet date, soit un datetime
            if type(ddd) is datetime:
                dt = ddd.replace(tzinfo=timezone.utc)
                setattr(self, param, dt)
                self.is_all_day = False
            elif type(ddd) is date:
                setattr(self, param, ddd)
                self.is_all_day = True

        if "LAST-MODIFIED" in component:
            self.updated = component.decoded("LAST-MODIFIED")

        self.id = component.get("uid")+"" # avoid vText()

def to_ics(c_event):
    # convert calscync event to ical event

    e = Event()
    e.add('summary', c_event.subject)

    for param in ["start", "end"]:
        dd = getattr(c_event, param)  # date or datetime
        e.add('dt' + param, dd)

    e.add('uid', c_event.id)
    if c_event.updated:
        e.add('LAST-MODIFIED', c_event.updated)

    return e