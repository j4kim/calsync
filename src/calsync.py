from calsync_calendar import VirtualCalendar
from ics_calendar import IcsCalendar, OnlineIcsCalendar
from google_calendar import GoogleCalendar
from exchange_calendar import ExchangeCalendar
from datetime import datetime
import json, argparse, time, sys


def run(config_file):
    """Run the synchronisation process depending on the conguration file"""

    # open the configuration json file and close it at the end of the bloc
    with open(config_file, encoding="utf-8") as f:
        # dictionnary that will contain calendars defined in configuration files
        calendars = {}
        # loads the config as a python dictionnary
        config = json.loads(f.read())
        # create calendars from the definitions in config
        for key, params in config["definitions"].items():
            if params["type"] == "ics":
                if "url" in params:
                    calendars[key] = OnlineIcsCalendar(key, params["url"])
                else:
                    calendars[key] = IcsCalendar(key, params["path"])
            elif params["type"] == "google":
                calendars[key] = GoogleCalendar(key, params.get("id","primary"), params.get("futureOnly", False))
            elif params["type"] == "exchange":
                calendars[key] = ExchangeCalendar(key, params["server"], params["username"], params["address"])
            elif params["type"] == "virtual":
                # create a virtual calendar (not linked to any API)
                calendars[key] = VirtualCalendar(key)
            else:
                print("Configuration error : unknown type " + params["type"])
                sys.exit()
        print("{:*<53}".format("Definitions "))
        # print all events of each calendars
        for k, cal in calendars.items():
            print(cal)

        # we got the calendars and events, now we apply the rules defined in config
        for i, rule in enumerate(config["rules"]):
            print("\n{:*^53}".format(" Rule {} ".format(i+1)))
            print("{} <- {} {}".format(
                rule["destination"],
                rule["operation"],
                rule["operands"]
            ))
            if rule["operation"] == "union":
                dest = calendars[rule["destination"]]
                # append the events in operands to the dest calendar
                for name in rule["operands"]:
                    dest.join(calendars[name])
                # if a subject is defined, override all subjects before to write events
                if "subject" in rule:
                    dest.override_subject(rule["subject"])
                # write all the events in destination calendar, like in google,
                # exchange or just an ics file depending on the type of the calendar
                dest.write_events()
            else:
                print("unknown operation " + rule["operation"])


if __name__ == "__main__":
    # run("calsync.conf.json")
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

    # pretty credits print
    for info in ["", " Calsync v1.0 ", " Joaquim Perez ", " Haute-École Arc - Ingéniere ", " 27.01.2017 ", ""]:
        print("{:~^53}".format("{}".format(info)))

    if args.justonce:
        run(args.path)
    else:
        # run synchronisation, then wait 5 minutes and rerun it, etc... until the user quit the program
        while True:
            print("Calsync syncing {}".format(datetime.now().strftime("the %d.%m.%Y at %H:%M:%S")))
            run(args.path)
            print("Wait {} seconds\n\n".format(args.refreshtime))
            time.sleep(args.refreshtime)
