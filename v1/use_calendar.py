from calsync_calendar import CalsyncCalendar
from ics_calendar import IcsCalendar
from google_calendar import GoogleCalendar
from exchange_calendar import ExchangeCalendar
import json

def main():
    with open("g_to_g.conf.json", encoding="utf-8") as f:
        calendars = {}
        config = json.loads(f.read())
        print("{:*<53}".format("Definitions "))
        for key, params in config["definitions"].items():
            if params["type"] == "ics":
                calendars[key] = IcsCalendar(key, params["path"])
            elif params["type"] == "google":
                calendars[key] = GoogleCalendar(key, params["id"])
            elif params["type"] == "exchange":
                calendars[key] = ExchangeCalendar(key, params["server"], params["username"], params["address"])
            else:
                print("unknown type " + params["type"])
        for k, cal in calendars.items():
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
            elif rule["operation"] == "intersection":
                pass
            else:
                print("unknown operation " + rule["operation"])


if __name__ == "__main__":
    main()

    # from calsync_event import CalsyncEvent
    # e1 = CalsyncEvent()
    # e1.id = "1234"
    # e1.subject = "coucou"
    #
    # e2 = CalsyncEvent()
    # e2.id = "5678"
    # e2.subject = "hello"
    #
    # cal = CalsyncCalendar("Abstract calendar")
    # cal.add(e1)
    # cal.add(e2)
    #
    # other_e2 = CalsyncEvent()
    # other_e2.id = "5678"
    # other_e2.subject = "salut"
    #
    # cal.add(other_e2)
    #
    # print(cal)