# -*- coding: utf-8 -*-

from icalendar import Calendar


def save(cal, filename): 
    f = open(filename, 'wb')
    f.write(cal.to_ical())
    f.close()


def print_property_items(cal):
    for k,v in cal.property_items():
        print(str(k) + "  ->  " + str(v))


def print_events(cal):
    for component in cal.walk():
        if component.name == "VEVENT":
            print("Event : " + component.get("summary"))
            print("Starts at " + str(component.decoded("dtstart")))
            print("Ends at " + str(component.decoded("dtend")))
            print("last modified : " + str(component.decoded("LAST-MODIFIED")))
            print("ID : " + component.get("uid"))
            print("***")


def read_ics(ics_text):
    cal = Calendar.from_ical(ics_text)
    # print(cal)
    # print_property_items(cal)
    print_events(cal)
    # save(cal, './example_copy.ics')


    
if __name__ == "__main__":
    with open('./agenda_test_updated.ics', 'r') as f:
        read_ics(f.read())