from datetime import date, datetime, timezone

import icalendar
from icalendar import vDatetime, vDate, vDDDTypes, Event

from google_api_tools import get_service


class Calendar:
    """Classe représeantant un calendrier abstrait"""

    def __init__(self):
        self.events = []

    def print_events(self):
        if not self.events:
            print('No upcoming events found.')
        for event in self.events:
            # récupère la date et l'heure si dispo, sinon seulement la date
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])


class IcsCalendar(Calendar):
    def __init__(self, ics_path):
        Calendar.__init__(self)
        with open(ics_path, encoding="utf-8") as ics_text:
            self.ical = icalendar.Calendar.from_ical(ics_text.read())

    def read_events(self):
        for component in self.ical.walk():
            if component.name == "VEVENT":
                event = {}
                event["summary"] = component.get("summary")+"" # avoid vText()

                for param in ["start","end"]:
                    event[param] = {}
                    d = component.get('dt'+param)
                    ddd = vDDDTypes.from_ical(d)
                    if type(ddd) is datetime:
                        event[param]["dateTime"] = str(ddd.isoformat())
                    elif type(ddd) is date:
                        event[param]["date"] = str(ddd)

                self.events.append(event)

    def write_event(self, event):
        e = Event()
        e.add('summary', event['summary'])

        for param in ["start","end"]:
            d_str = event[param].get('dateTime', event[param].get('date'))
            date = datetime.strptime(d_str, "%Y-%m-%d")
            e.add('dt'+param, date)

        self.ical.add_component(e)

        with open('./out.ics', 'wb') as f:
            f.write(self.ical.to_ical())


class GoogleCalendar(Calendar):
    def __init__(self, id="primary"):
        Calendar.__init__(self)
        self.service = get_service()
        self.id = id
        self.calendar = self.service.calendars().get(calendarId=id).execute()

    def read_events(self):
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        eventsResult = self.service.events().list(
            calendarId=self.id, singleEvents=True,
            orderBy='startTime').execute()
        self.events = eventsResult.get('items', [])

    def list_calendars(self):
        page_token = None
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                print(calendar_list_entry['summary'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

    def write_event(self, event):
        event['summary'] += " (Calsync)"
        e = self.service.events().insert(calendarId=self.id, body=event).execute()
        print('Event created: %s' % (e.get('htmlLink')))
