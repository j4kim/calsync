from calsync_calendar import IcsCalendar, GoogleCalendar
import json

if __name__ =="__main__":

	with open("calsync.conf.json", encoding="utf-8") as f:
		calendars={}
		config = json.loads(f.read())
		for key,params in config["definitions"].items():
			if params["type"] == "ics":
				calendars[key]=(IcsCalendar(params["path"]))
			elif params["type"] == "google":
				calendars[key]=(GoogleCalendar(params["id"]))
		for k,cal in calendars.items():
			print(k)
			cal.read_events()
			cal.print_events()
		for i,rule in enumerate(config["rules"]):
			print("rule {} : {} = {} {} {}".format(
				i,
				rule["destination"],
				rule["operands"][0],
				rule["operation"],
				rule["operands"][1]
				)
			)
