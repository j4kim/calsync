import datetime

import httplib2
import icalendar
from googleapiclient import discovery

from google_api_tools import get_credentials


class Calendar:
    """Classe représeantant un calendrier abstrait"""
    def __init__(self):
        self.events=[]

    def print_events(self):
        if not self.events:
            print('No upcoming events found.')
        for event in self.events:
            start = event['start'].get('dateTime')
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
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)

    def read_events(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        eventsResult = self.service.events().list(
            calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        self.events = eventsResult.get('items', [])
