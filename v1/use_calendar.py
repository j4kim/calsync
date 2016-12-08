from calsync_calendar import IcsCalendar, GoogleCalendar
import json

if __name__ == "__main__":

    with open("./calsync.conf.json", encoding="utf-8") as f:
        calendars = {}
        config = json.loads(f.read())
        print("Definitions :")
        for key, params in config["definitions"].items():
            if params["type"] == "ics":
                calendars[key] = (IcsCalendar(params["path"]))
            elif params["type"] == "google":
                calendars[key] = (GoogleCalendar(params["id"]))
        for k, cal in calendars.items():
            print("{} ({})".format(k, cal.__class__.__name__))
            cal.read_events()
            cal.print_events()

        print("Rules :")
        for i, rule in enumerate(config["rules"]):
            print("rule {} : {} = {} {} {}".format(
                i,
                rule["destination"],
                rule["operands"][0],
                rule["operation"],
                rule["operands"][1]
            ))

        #e1 = calendars["B"].events[0]
        #e2 = calendars["A"].events[0]
        #calendars["C"].write_event(e1)
        #calendars["C"].write_event(e2)

        e = {
            'start': {
                'date': '2016-12-20'
            },
            'end': {
                'date': '2016-12-21'
            },
            'summary': 'Yolo'
        }
        #calendars['B'].write_event(e)

        for e in calendars['A'].events:
            calendars['B'].write_event(e)
