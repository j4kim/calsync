from calsync_calendar import CalsyncCalendar
from google_api_tools import get_service
from google_event import GoogleEvent, to_google


class GoogleCalendar(CalsyncCalendar):
    def __init__(self, name, id="primary"):
        CalsyncCalendar.__init__(self, name)
        self.id = id
        self.service = get_service()
        super().read_events()

    def read_events(self):
        eventsResult = self.service.events().list(
            calendarId=self.id, singleEvents=True,
            orderBy='startTime').execute()
        g_events = eventsResult.get('items', [])

        for e in g_events:
            g = GoogleEvent(e)
            self.events[g.id] = g
            # print(g)

    def create_event(self, event):
        self.service.events().import_(
            calendarId=self.id,
            body = to_google(event)
        ).execute()

    def update_event(self, event):
        self.service.events().update(
            calendarId = self.id,
            eventId = event.google_id,
            body = to_google(event)
        ).execute()

    def delete_event(self, google_id):
        try:
            response = self.service.events().delete(
                calendarId = self.id,
                eventId = google_id
            ).execute()
            if not response:
                print("event with id {} deleted".format(google_id))
        except:
            print("event width id {} has already been deleted")