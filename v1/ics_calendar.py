from datetime import datetime, timezone
import icalendar
from icalendar import vDDDTypes, Event
from calsync_calendar import CalsyncCalendar

class IcsCalendar(CalsyncCalendar):
    def __init__(self, name, ics_path):
        CalsyncCalendar.__init__(self, name)
        self.path = ics_path
        try:
            with open(self.path, encoding="utf-8") as ics_text:
                self.ical = icalendar.Calendar.from_ical(ics_text.read())
                self.read_events()
        except FileNotFoundError:
            # if the ics file does not exists, it will be created in write_events
            pass

    def read_events(self):
        for component in self.ical.walk():
            if component.name == "VEVENT":

                event = {}
                event["summary"] = component.get("summary")+"" # avoid vText()

                for param in ["start","end"]:
                    d = component.get('dt'+param) # on ne sait pas si date ou datetime
                    event[param] = vDDDTypes.from_ical(d) # retourne soit un objet date, soit un datetime
                    if type(event[param]) is datetime:
                        event[param] = event[param].replace(tzinfo=timezone.utc) # todo: récupérer le fuseau depuis le calendrier

                if "LAST-MODIFIED" in component:
                    event["updated"] = component.decoded("LAST-MODIFIED")

                uid = component.get("uid")+"" # avoid vText()
                event["iCalUID"] = uid
                self.events[uid] = event

    def write_events(self):
        self.ical = icalendar.Calendar()
        for uid, event in self.events.items():
            self.write_event(event)
        with open(self.path, 'wb') as f:
            f.write(self.ical.to_ical())
            print("events written")


    def write_event(self, event):

        # convert calscync event to ical event

        e = Event()
        e.add('summary', event['summary'])

        for param in ["start","end"]:
            dd = event[param] # date or datetime
            e.add('dt'+param, dd)

        e.add('uid', event["iCalUID"]);
        if "updated" in event:
            e.add('LAST-MODIFIED', event["updated"])

        self.ical.add_component(e)
