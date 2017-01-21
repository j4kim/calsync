from datetime import date, datetime, timedelta
from google_api_tools import get_service
import dateutil.parser
from copy import deepcopy
from calsync_calendar import CalsyncCalendar

class GoogleCalendar(CalsyncCalendar):
    def __init__(self, name, id="primary"):
        CalsyncCalendar.__init__(self, name)
        self.id = id
        self.service = get_service()
        self.read_events()

    def read_events(self):
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
            # # Désolé Yoan Blanc si vous voyez ça
            # if "extendedProperties" in e:
            #     if "private" in e["extendedProperties"]:
            #         if "exchange_id" in  e["extendedProperties"]["private"]:
            #             e["exchange_id"] = e["extendedProperties"]["private"]["exchange_id"]
            #             e["changekey"] = e["extendedProperties"]["private"]["changekey"]
            del e['organizer'] # avoid HttpError 400 when requesting https://... returned "The owner of the calendar must either be the organizer or an attendee of an event that is imported."
            self.events[e["iCalUID"]] = e


    # insert or update events
    def write_events(self):
        for uid, event in self.events.items():
            self.write_event(event)

    def write_event(self, event):
        if 'flags' in event and event["flags"]:
            # transforme le calsync Event en google Event
            g_event = GoogleCalendar.to_google_event(event)
            #print("event to write", g_event)
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

        if "updated" in g_event:
            g_event["updated"] += timedelta(microseconds=1)  # je rajoute une microsecondes pour que google m'emmerde pas avec des formats de date incorrects
            # googleapiclient.errors.HttpError: <HttpError 400 when requesting https://... returned "Invalid value for: Invalid format: "2017-01-03T16:55:02Z" is malformed at "Z"">

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

        # if "exchange_id" in g_event:
        #     g_event["extendedProperties"] = {
        #         "private": {
        #             "exchange_id": g_event["exchange_id"],
        #             "changekey": g_event["changekey"]
        #         }
        #     }

        # l'api google n'arrive pas à convertir un set python en json, il faut enlever les flags
        # TypeError: {'is_new'} is not JSON serializable
        if 'flags' in g_event: del g_event['flags']
        return g_event
