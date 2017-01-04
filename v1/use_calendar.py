from calsync_calendar import IcsCalendar, GoogleCalendar, CalsyncCalendar
import json

if __name__ == "__main__":

    with open("./calsync.conf.json", encoding="utf-8") as f:
        calendars = {}
        config = json.loads(f.read())
        print("Definitions :")
        for key, params in config["definitions"].items():
            if params["type"] == "ics":
                calendars[key] = (IcsCalendar(key, params["path"]))
            elif params["type"] == "google":
                calendars[key] = (GoogleCalendar(key, params["id"]))
        for k, cal in calendars.items():
            #cal.read_events()
            print(cal)

        print("Rules :")
        for i, rule in enumerate(config["rules"]):
            print("rule {} : {} = {} {}".format(
                i,
                rule["destination"],
                rule["operands"],
                rule["operation"]
            ))
            if rule["operation"] == "union":
                dest = rule["destination"]
                for cal in rule["operands"]:
                    calendars[dest].join(calendars[cal])
                calendars[dest].write_events()