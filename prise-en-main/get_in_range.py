from icalendar import Calendar
import sys
from datetime import datetime, timezone


def print_event(component):
    print("Event : " + component.get("summary"))
    print("Starts at " + str(component.decoded("dtstart")))
    print("Ends at " + str(component.decoded("dtend")))
    print("last modified : " + str(component.decoded("LAST-MODIFIED")))
    print("ID : " + component.get("uid"))
    print("***")


# sorte de décorateur ? Pour chaque évènement du calendrier cal, appelle la fonction func
def for_each_event(cal, func):
    for component in cal.walk():
        if component.name == "VEVENT":
            func(component)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("need arguments : file.ics [date1] [date2]")
        print("date format : dd.mm.yyyy")
        print("default are date1:now date2:infinity")
        sys.exit(-1)

    try:
        f = open(sys.argv[1], 'r', encoding="utf-8")
        cal = Calendar.from_ical(f.read())
    except FileNotFoundError:
        print("File " + sys.argv[1] + " not found")
        sys.exit(-2)

    # il faut que les dates soient "aware" pour les comparer
    # c'est à dire qu'il faut qu'elles aient leur zone horaire (tzinfo)
    date1 = datetime.now(timezone.utc)
    date2 = datetime.max.replace(tzinfo=timezone.utc)

    if len(sys.argv) > 2:
        try:
            date1 = datetime.strptime(sys.argv[2], '%d.%m.%Y').replace(tzinfo=timezone.utc)
            if len(sys.argv) > 3:
                date2 = datetime.strptime(sys.argv[3], '%d.%m.%Y')
                # fin de journée comme ça la date de fin est comprise dans l'intervalle
                date2 = date2.replace(tzinfo=timezone.utc, hour=23, minute=59, second=59)
        except ValueError:
            print("date format error")
            sys.exit()


    def print_event_if_in_range(component):
        eventStart = component.decoded("dtstart")
        if eventStart > date1 and eventStart < date2:
            print_event(component)


    for_each_event(cal, print_event_if_in_range)
