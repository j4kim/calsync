from calsync_calendar import CalsyncCalendar
from ics_calendar import IcsCalendar
from google_calendar import GoogleCalendar
import json

if __name__ == "__main__":

    with open("./calsync.conf.json", encoding="utf-8") as f:
        calendars = {}
        config = json.loads(f.read())
        print("{:*<53}".format("Definitions "))
        for key, params in config["definitions"].items():
            if params["type"] == "ics":
                calendars[key] = (IcsCalendar(key, params["path"]))
            elif params["type"] == "google":
                calendars[key] = (GoogleCalendar(key, params["id"]))
        for k, cal in calendars.items():
            #cal.read_events()
            print(cal)

        for i, rule in enumerate(config["rules"]):
            print("{:*^53}".format(" Rule {} ".format(i+1)))
            print("{} <- {} {}".format(
                rule["destination"],
                rule["operation"],
                rule["operands"]
            ))
            if rule["operation"] == "union":
                dest = calendars[rule["destination"]]
                for name in rule["operands"]:
                    dest.join(calendars[name])
                dest.write_events()
