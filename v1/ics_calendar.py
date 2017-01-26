import icalendar

from calsync_calendar import CalsyncCalendar
from ics_event import IcsEvent, to_ics


class IcsCalendar(CalsyncCalendar):
    def __init__(self, name, ics_path):
        CalsyncCalendar.__init__(self, name)
        self.path = ics_path
        try:
            with open(self.path, encoding="utf-8") as ics_text:
                self.ical = icalendar.Calendar.from_ical(ics_text.read())
                super().read_events()
        except FileNotFoundError:
            # if the ics file does not exists, it will be created in write_events
            pass

    def read_events(self):
        for component in self.ical.walk():
            if component.name == "VEVENT":
                i = IcsEvent(component)
                self.events[i.id] = i

    def write_events(self):
        self.ical = icalendar.Calendar()
        for uid, event in self.events.items():
            self.ical.add_component(to_ics(event))
        with open(self.path, 'w') as f:
            f.write(self.ical.to_ical().decode("utf-8"))
            print("events written")
