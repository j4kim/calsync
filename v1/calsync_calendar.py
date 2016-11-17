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

	def __init__(self, ics_path):
		Calendar.__init__(self)
		with open(ics_path, encoding="utf-8") as ics_text:
			self.ical = icalendar.Calendar.from_ical(ics_text.read())


	def read_events(self):
		for component in self.ical.walk():
			if component.name == "VEVENT":
				event={}
				event["summary"] = component.get("summary")
				event["start"]={}
				event["start"]["dateTime"] = str(component.decoded("dtstart"))
				self.events.append(event)

# pas une si bonne idée car readonly				
# class OnlineIcsCalendar(IcsCalendar):

	# def __init__(self, url):
		# Calendar.__init__(self)
		# import urllib.request
		# self.ical = icalendar.Calendar.from_ical(urllib.request.urlopen(url).read())
		

class GoogleCalendar(Calendar):
	def __init__(self, id="primary"):
		Calendar.__init__(self)
		self.service = get_service()
		self.id=id
		self.calendar = self.service.calendars().get(calendarId=id).execute()

	def read_events(self):
		now = datetime.datetime.utcnow().isoformat() + 'Z'	# 'Z' indicates UTC time
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
