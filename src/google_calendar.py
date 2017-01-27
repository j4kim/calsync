import sys

from calsync_calendar import CalsyncCalendar
from google_api_tools import get_service
from google_event import GoogleEvent, to_google

class GoogleCalendar(CalsyncCalendar):
    """Implementation of CalsyncCalendar able to communicate with the Google Calendar API"""

    def __init__(self, name, id="primary"):
        """Initialize a Google calendar and launch the authentication flow"""
        CalsyncCalendar.__init__(self, name)
        self.id = id
        # authorize the user and construct a resource for interacting with the API
        self.service = get_service()
        # calls the calsync_calendar.read_events method
        super().read_events()

    def read_events(self):
        """Reads all the events from the Google Calendar API, then convert them to a CalsyncEvent representation"""
        try:
            eventsResult = self.service.events().list(
                calendarId=self.id, singleEvents=True,
                orderBy='startTime').execute()
        except:
            print("Error : unable to connect to Google calendar with id "+self.id)
            sys.exit()

        # a dictionnary containing all events, an event is also a dictionnary (parsed from json)
        g_events = eventsResult.get('items', [])

        for e in g_events:
            # create a calsync compatible representation of the events and add it to self.events
            g = GoogleEvent(e)
            self.events[g.id] = g

    def create_event(self, event):
        """Convert the event given in a Google-friendly representation and upload it"""
        self.service.events().import_(
            calendarId=self.id,
            body = to_google(event)
        ).execute()

    def update_event(self, event):
        """Convert the event given in a Google-friendly representation and update it"""
        self.service.events().update(
            calendarId = self.id,
            eventId = event.google_id,
            body = to_google(event)
        ).execute()

    def delete_event(self, id):
        """Check if the id given is in the current calendar, then try to destroy it in the API"""
        if id not in self.events: return
        google_id = self.events[id].google_id
        try:
            response = self.service.events().delete(
                calendarId = self.id,
                eventId = google_id
            ).execute()
            if not response:
                print("Event {} deleted".format(self.events[id].subject))
        except:
            # print("Event width id {} has already been deleted")
            pass