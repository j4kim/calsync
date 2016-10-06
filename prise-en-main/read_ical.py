# -*- coding: utf-8 -*-

from icalendar import Calendar
    
def save(cal, filename): 
    f = open(filename, 'wb')
    f.write(cal.to_ical())
    f.close()
    
def read_ics(ics_text):
    cal = Calendar()
    cal = Calendar.from_ical(ics_text)
    for k,v in cal.property_items():
        print(str(k) +"  ->  " + str(v))
    #save(cal, './example_copy.ics')

    
    
with open('./example.ics', 'r') as f:
    read_ics(f.read())