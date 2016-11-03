from calsync_calendar import IcsCalendar, GoogleCalendar

if __name__ =="__main__":

    cal = IcsCalendar()
    cal.read_events("../prise-en-main/agenda_test_initial.ics")
    cal.print_events()

    cal2 = GoogleCalendar()
    cal2.read_events()
    cal2.print_events()
