from datetime import date, datetime, timezone

import icalendar
from icalendar import vDatetime, vDate, vDDDTypes, Event

from google_api_tools import get_service
import dateutil.parser
from copy import deepcopy

class Calendar:
    """Classe représeantant un calendrier abstrait"""

    def __init__(self):
        # dictionnaire avec clé:uid d'un event et valeur:CalsyncEvent
        self.events = {}

    def print_events(self):
        if not self.events:
            print('No upcoming events found.')
        for uid, event in self.events.items():
            start = event['start']
            print(start, event['summary'])

    def is_new(self, uid):
        # check if event does not already exists
        return uid not in self.events:

    def is_updated(self, uid, update_datetime)
        # if the event exists, check if the updated datetime has changed
        return self.events[uid]["updated"] < update_datetime




class IcsCalendar(Calendar):
    def __init__(self, ics_path):
        Calendar.__init__(self)
        self.path = ics_path
        with open(self.path, encoding="utf-8") as ics_text:
            self.ical = icalendar.Calendar.from_ical(ics_text.read())
            self.read_events()

    def read_events(self):
        for component in self.ical.walk():
            if component.name == "VEVENT":

                event = {}
                event["summary"] = component.get("summary")+"" # avoid vText()

                for param in ["start","end"]:
                    d = component.get('dt'+param) # on ne sait pas si date ou datetime
                    event[param] = vDDDTypes.from_ical(d) # retourne soit un objet date, soit un datetime

                event["updated"] = component.decoded("LAST-MODIFIED")

                uid = component.get("uid")+"" # avoid vText()
                event["iCalUID"] = uid
                self.events[uid] = event


    def write_event(self, event):
        e = Event()
        e.add('summary', event['summary'])

        for param in ["start","end"]:
            dd = event[param] # date or datetime
            e.add('dt'+param, dd)

        e.add('uid', event["iCalUID"]);
        e.add('LAST-MODIFIED', event["updated"])

        if self.is_new(uid):
            self.ical.add_component(e)
            with open(self.path + ".out", 'wb') as f:
                f.write(self.ical.to_ical())
        else:
            print("l'event existe deja")




class GoogleCalendar(Calendar):
    def __init__(self, id="primary"):
        Calendar.__init__(self)
        self.service = get_service()
        self.id = id
        self.calendar = self.service.calendars().get(calendarId=id).execute()
        self.read_events()

    def read_events(self):
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        eventsResult = self.service.events().list(
            calendarId=self.id, singleEvents=True,
            orderBy='startTime').execute()
        g_events = eventsResult.get('items', [])

        for e in g_events:
            e["updated"] = dateutil.parser.parse(e["updated"]) # convertit la str en datetime
            self.events[e["iCalUID"]] = e

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

        print("event to write :", event)

        if self.is_new(event["iCalUID"]):
            # transforme le calsync Event en google Event
            g_event = GoogleCalendar.to_google_event(event)

            new_e = self.service.events().import_(calendarId=self.id, body=g_event).execute()
            print('Event created: %s' % (new_e.get('htmlLink')))
        else:
            print("Event already exists")

    @staticmethod
    def to_google_event(event):
        g_event = deepcopy(event)

        # updated : datetime -> yyyy-mm-ddThh:mm:ss.xxxZ
        g_event["updated"] = g_event["updated"].replace(tzinfo=None).isoformat() + '.0Z'
        # start : date|datetime -> {"dateTime": "yyyy-mm-ddThh:mm:ss+01:00"}|{"date": "yyyy-mm-dd"}
        # end : date|datetime -> {"dateTime": "yyyy-mm-ddThh:mm:ss+01:00"}|{"date": "yyyy-mm-dd"}
        for param in ["start", "end"]:
            d = {}
            if type(g_event[param]) is date:
                d["date"] = g_event[param].isoformat()
            elif type(g_event[param]) is datetime:
                d["dateTime"] = g_event[param].isoformat()
            g_event[param] = d

        return g_event

