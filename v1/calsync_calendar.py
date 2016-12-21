from datetime import date, datetime, timezone

import icalendar
from icalendar import vDatetime, vDate, vDDDTypes, Event

from google_api_tools import get_service
import dateutil.parser

class Calendar:
    """Classe représeantant un calendrier abstrait"""

    def __init__(self):
        self.events = []
        # dictionnaire avec clé:uid d'un event et valeur:date de modification
        self.events_uids = {}

    def print_events(self):
        if not self.events:
            print('No upcoming events found.')
        for event in self.events:
            # récupère la date et l'heure si dispo, sinon seulement la date
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    def is_new(self, uid):
        return uid not in self.events_uids

    # TODO
    def is_new_or_updated(self, uid):
        return self.is_new(uid)




class IcsCalendar(Calendar):
    def __init__(self, ics_path):
        Calendar.__init__(self)
        self.path = ics_path
        with open(self.path, encoding="utf-8") as ics_text:
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

                uid = component.get("uid")+"" # avoid vText()
                updated = component.decoded("LAST-MODIFIED").replace(tzinfo=None) # google veut du na!ive pour ça
                self.events_uids[uid] = updated # datetime object
                event["iCalUID"] = uid
                event["updated"] = updated.isoformat() + '.000Z' # c'est dla merde mais j'en ai vraiment marre
                print("yo "+event["updated"])

                self.events.append(event)

    def write_event(self, event):
        e = Event()
        e.add('summary', event['summary'])

        for param in ["start","end"]:
            d_str = event[param].get('dateTime', event[param].get('date'))
            date = datetime.strptime(d_str, "%Y-%m-%d")
            e.add('dt'+param, date)

        uid = event["iCalUID"]
        e.add('uid', uid);
        e.add('LAST-MODIFIED', dateutil.parser.parse(event["updated"]))

        if self.is_new_or_updated(uid):
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

        if self.is_new_or_updated(event["iCalUID"]):
            event['summary'] += " (Calsync)"
            e = self.service.events().insert(calendarId=self.id, body=event).execute()
            print('Event created: %s' % (e.get('htmlLink')))
        else:
            print("l'event existe deja")
