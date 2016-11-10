import datetime

import icalendar

from google_api_tools import get_service


class Calendar:
    """Classe représeantant un calendrier abstrait"""
    def __init__(self):
        self.events=[]

    def print_events(self):
        if not self.events:
            print('No upcoming events found.')
        for event in self.events:
            # récupère la date et l'heure si dispo, sinon seulement la date
            start = event['start'].get('dateTime',event['start'].get('date'))
            print(start, event['summary'])


class IcsCalendar(Calendar):

    def read_events(self, ics_path):
        with open(ics_path, encoding="utf-8") as ics_text:
            cal = icalendar.Calendar.from_ical(ics_text.read())
            for component in cal.walk():
                if component.name == "VEVENT":
                    event={}
                    event["summary"] = component.get("summary")
                    event["start"]={}
                    event["start"]["dateTime"] = str(component.decoded("dtstart"))
                    self.events.append(event)


class GoogleCalendar(Calendar):
    def __init__(self):
        self.service = get_service()

    def read_events(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        eventsResult = self.service.events().list(
            calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        self.events = eventsResult.get('items', [])
