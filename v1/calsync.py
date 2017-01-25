from ics_calendar import IcsCalendar
from google_calendar import GoogleCalendar
from exchange_calendar import ExchangeCalendar
import json

def run(config_file):
    with open(config_file, encoding="utf-8") as f:
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
            print("\n{:*^53}".format(" Rule {} ".format(i+1)))
            print("{} <- {} {}".format(
                rule["destination"],
                rule["operation"],
                rule["operands"]
            ))
            if rule["operation"] == "union":
                dest = calendars[rule["destination"]]
                for name in rule["operands"]:
                    dest.join(calendars[name])
                if "subject" in rule:
                    dest.override_subject(rule["subject"])
                dest.write_events()
            elif rule["operation"] == "intersection":
                pass
            else:
                print("unknown operation " + rule["operation"])


if __name__ == "__main__":
    import argparse, time, sys
    from datetime import datetime

    # run("configurations/g_to_g_anonymous.conf.json")
    # sys.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument("path",
                        help="Configuration file name")
    parser.add_argument("-t", "--refreshtime",
                        help="Syncing period in seconds (default: 300s == 5 minutes)",
                        type=int,
                        default=300)
    parser.add_argument("-o", "--justonce",
                        help="Add this if you want calsync to be executed just once",
                        action="store_true",
                        default=False)
    args = parser.parse_args()

    if args.justonce:
        run(args.path)
    else:
        while True:
            print("Calsync syncing {}".format(datetime.now().strftime("%A the %d. %B %Y at %H:%M:%S")))
            run(args.path)
            print("Wait {} seconds\n\n".format(args.refreshtime))
            time.sleep(args.refreshtime)
