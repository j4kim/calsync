from icalendar import Calendar


def print_event(component):
    print("Event : " + component.get("summary"))
    print("Starts at " + str(component.decoded("dtstart")))
    print("Ends at " + str(component.decoded("dtend")))
    print("last modified : " + str(component.decoded("LAST-MODIFIED")))
    print("ID : " + component.get("uid"))
    print("***")


def for_each_event(cal, func):
    for component in cal.walk():
        if component.name == "VEVENT":
            func(component)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("need 2 arguments : file1.ics file2.ics")
        sys.exit(-1)
    cals = []
    for i in 0,1:
        try:
            f = open(sys.argv[i+1], 'r', encoding="utf-8")
            cals.append(Calendar.from_ical(f.read()))
        except FileNotFoundError:
            print("File " + sys.argv[i + 1] + " not found")
            sys.exit(-2)

    # print("INITIAL CALENDAR : ")
    # for_each_event(cals[0], print_event)
    # print("UPDATED CALENDAR : ")
    # for_each_event(cals[1], print_event)

    # dictionnaire avec clé:uid d'un event et valeur:date de modification
    events_uids = {}

    def add_event_uid(component):
        events_uids[component.get("uid")] = component.decoded("LAST-MODIFIED")

    for_each_event(cals[0], add_event_uid)


    def get_if_new_event(component):
        if component.get("uid") in events_uids:
            print("l'évènemnt " + component.get("summary") + " existait déjà")
            return False
        else:
            print("l'évènemnt " + component.get("summary") + " est nouveau")
            return True

    #for_each_event(cals[1], get_if_new_event)

    def get_if_new_or_updated(component):
        if get_if_new_event(component):
            return True
        else:
            if events_uids[component.get("uid")] == component.decoded("LAST-MODIFIED"):
                print("\tl'évènemnt n'a pas été modifié")
                return False
            else:
                print("\tl'évènemnt a été modifié")
                return True

    for_each_event(cals[1], get_if_new_or_updated)