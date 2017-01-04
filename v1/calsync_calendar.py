from datetime import date, datetime, timezone, timedelta

import icalendar
from icalendar import vDatetime, vDate, vDDDTypes, Event

from google_api_tools import get_service
import dateutil.parser
from copy import deepcopy

class CalsyncCalendar:
    """Classe représentant un calendrier abstrait"""

    def __init__(self):
        # dictionnaire avec clé:uid d'un event et valeur:dictionnaire représentant un event
        self.events = {}

    def __repr__(self):
        s = "{:_^53}".format(" CALENDAR {} ".format(self.name))
        s += "\n{:^53}".format(self.__class__.__name__)
        s += "\n{:^25} + {:^25}".format(" date ", " summary ")
        if not self.events:
            s += '\nNo events found.'
        for uid, event in self.events.items():
            start = event['start']
            s += "\n{:<25} : {}".format(str(start), event["summary"])
            # s += " // {} / {} / {}".format(event["updated"],  event["iCalUID"], event.get("id","pas d'id"))
        return s

    def union(self, cal1, cal2):
        self.join(cal1)
        self.join(cal2)
        self.write_events()

    # add all events of other_cal to self (only if events are new or updated)
    def join(self, other_cal):
        for uid, event in other_cal.events.items():
            self.add(event)

    # idempotent addition
    def add(self, event):
        # reinitialize flags
        event["flags"] = set()
        uid = event["iCalUID"]
        # check if event does not already exists
        if uid not in self.events:
            # raise a flag to know that we have to create this event
            event['flags'].add("is_new")
            self.events[uid] = event

        # if the event exists, check if the last-update datetime has changed
        elif self.events[uid]["updated"] < event["updated"]:
            # if the event has been updated, replace it in the dictionnary
            # raise a flag for Google calendars update method instead of import
            event['flags'].add("has_been_updated")
            # bricolage pour permettre l'update par la google api qui a besoin de l'attribut id
            if "id" in self.events[uid]:
                event["id"] = self.events[uid]["id"]
            self.events[uid] = event




class IcsCalendar(CalsyncCalendar):
    def __init__(self, name, ics_path):
        CalsyncCalendar.__init__(self)
        self.name = name
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
                    if type(event[param]) is datetime:
                        event[param] = event[param].replace(tzinfo=timezone.utc) # todo: récupérer le fuseau depuis le calendrier

                event["updated"] = component.decoded("LAST-MODIFIED")
                event["updated"] += timedelta(microseconds=1) # je rajoute une microsecondes pour que google m'emmerde pas avec des formats de date incorrects
                # googleapiclient.errors.HttpError: <HttpError 400 when requesting https://www.googleapis.com/calendar/v3/calendars/3mnnljsfhcu14k8n398h9o4oh8%40group.calendar.google.com/events/import?alt=json returned "Invalid value for: Invalid format: "2017-01-03T16:55:02Z" is malformed at "Z"">

                uid = component.get("uid")+"" # avoid vText()
                event["iCalUID"] = uid
                self.events[uid] = event

    def write_events(self):
        self.ical = icalendar.Calendar()
        for uid, event in self.events.items():
            self.write_event(event)
        # with open(self.path + ".out", 'wb') as f:
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
        e.add('LAST-MODIFIED', event["updated"])

        self.ical.add_component(e)




class GoogleCalendar(CalsyncCalendar):
    def __init__(self, name, id="primary"):
        CalsyncCalendar.__init__(self)
        self.name = name
        self.id = id
        self.service = get_service()
        #self.calendar = self.service.calendars().get(calendarId=id).execute()
        self.read_events()

    def read_events(self):
        #now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        eventsResult = self.service.events().list(
            calendarId=self.id, singleEvents=True,
            orderBy='startTime').execute()
        g_events = eventsResult.get('items', [])

        for e in g_events:
            e["updated"] = dateutil.parser.parse(e["updated"]) # convertit la str en datetime
            for param in ["start", "end"]:
                # les events Google contiennent soit une date, soit une datetime pour les propriétés start et end
                if "dateTime" in e[param]:
                    e[param] = dateutil.parser.parse(e[param]["dateTime"]) # convertit la string en datetime
                elif "date" in e[param]:
                    e[param] = dateutil.parser.parse(e[param]["date"]).date() # convertit la string en datetime, puis ne récupère que la date
            del e['organizer'] # avoid HttpError 400 when requesting https://... returned "The owner of the calendar must either be the organizer or an attendee of an event that is imported."
            self.events[e["iCalUID"]] = e

    # def list_calendars(self):
    #     page_token = None
    #     while True:
    #         calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
    #         for calendar_list_entry in calendar_list['items']:
    #             print(calendar_list_entry['summary'])
    #         page_token = calendar_list.get('nextPageToken')
    #         if not page_token:
    #             break


    # insert or update events
    def write_events(self):
        for uid, event in self.events.items():
            self.write_event(event)

    def write_event(self, event):
        if 'flags' in event and event["flags"]:
            # transforme le calsync Event en google Event
            g_event = GoogleCalendar.to_google_event(event)
            # print("event to write", g_event)
            if "is_new" in event["flags"]:
                # call Google Calendar API's import method
                new_e = self.service.events().import_(calendarId=self.id, body=g_event).execute()
                print('Event "{}" created: {}'.format(new_e["summary"], new_e["htmlLink"]))
            elif "has_been_updated" in event["flags"]:
                # call Google Calendar API's update method
                updated_event = self.service.events().update(calendarId=self.id, eventId=event['id'], body=g_event).execute()
                print('Event "{}" updated: {}'.format(updated_event["summary"], updated_event["htmlLink"]))
        else:
            # if no flags are raised, there is nothing to do
            print('Event "{}" has not been updated'.format(event["summary"]))

    @staticmethod
    def to_google_event(event):
        g_event = deepcopy(event)

        # updated : datetime -> yyyy-mm-ddThh:mm:ss.xxxZ
        g_event["updated"] = g_event["updated"].replace(tzinfo=None).isoformat() + 'Z'
        # start : date|datetime -> {"dateTime": "yyyy-mm-ddThh:mm:ss+01:00"}|{"date": "yyyy-mm-dd"}
        # end : date|datetime -> {"dateTime": "yyyy-mm-ddThh:mm:ss+01:00"}|{"date": "yyyy-mm-dd"}
        for param in ["start", "end"]:
            d = {}
            if type(g_event[param]) is date:
                d["date"] = g_event[param].isoformat()
            elif type(g_event[param]) is datetime:
                d["dateTime"] = g_event[param].isoformat()
            g_event[param] = d

        # google n'accepte pas les attributs qu'il ne connaît pas, il faut l'enlever
        if 'flags' in g_event: del g_event['flags']
        return g_event

