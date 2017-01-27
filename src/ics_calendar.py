import icalendar

from calsync_calendar import CalsyncCalendar
from ics_event import IcsEvent, to_ics


class IcsCalendar(CalsyncCalendar):
    """Implementation of CalsyncCalendar that works with the icalendar format"""

    def __init__(self, name, ics_path):
        CalsyncCalendar.__init__(self, name)
        self.path = ics_path
        try:
            with open(self.path, encoding="utf-8") as ics_text:
                # loads all the ical file in an icalendar.Calendar object
                self.ical = icalendar.Calendar.from_ical(ics_text.read())
                # calls parents read_events method to get deleted events
                super().read_events()
        except FileNotFoundError:
            # if the ics file does not exists, it will be created in write_events
            pass

    def read_events(self):
        """Walk through icalendar components, convert all VEVENT components
        in a CalsyncEvent representation and store them in self.envents"""
        for component in self.ical.walk():
            if component.name == "VEVENT":
                i = IcsEvent(component)
                self.events[i.id] = i

    def write_events(self):
        """Recreate an empty icalendar.Calendar object,
        fill it with current events and then store it overriding the existing one"""
        self.ical = icalendar.Calendar()
        for uid, event in self.events.items():
            self.ical.add_component(to_ics(event))
        with open(self.path, 'wb') as f:
            f.write(self.ical.to_ical())
            print("events written")
