from datetime import datetime

from exchangelib import CalendarItem, EWSDateTime, EWSTimeZone

from calsync_event import CalsyncEvent

tz = EWSTimeZone.timezone('Europe/Copenhagen')

class ExchangeEvent(CalsyncEvent):
    def __init__(self, x_item):
        CalsyncEvent.__init__(self)

        if x_item.extern_id is not None:
            # the calsync-specific id is stored in the external_id property of the CalendarItem
            self.id = x_item.extern_id
        else:
            # if this CalendarItem have no external id, it means it just has been created
            # in exchange, so we can use the exchange id as a calsync id
            self.id = x_item.item_id

        # we need to store exchange id in case this event has to be updated in exchange
        self.exchange_id = x_item.item_id
        # the changekey is also requested in case of update
        self.changekey = x_item.changekey
        self.subject = x_item.subject

        if x_item.is_all_day:
            self.start = x_item.start.date()
            self.end = x_item.end.date()
            self.is_all_day = True
        else:
            # start and end are not datetime, but EWSDateTime objects, we need to convert them to datetime
            s, e = x_item.start, x_item.end
            # this is not good but I didn't find a better way to do that
            self.start = datetime(s.year, s.month, s.day, s.hour, s.minute, s.second, s.microsecond)
            self.end = datetime(e.year, e.month, e.day, e.hour, e.minute, e.second, e.microsecond)
            self.is_all_day = False


def to_exchange(c_event, x_calendar):
    """Convert a CalsyncEvent to an Exchange CalendarItem object"""
    x_item = CalendarItem(folder = x_calendar.account.calendar)
    x_item.account = x_calendar.account
    # if the event contain en exchange_id, we need to copy it (with the exchangekey)
    # to let know exchange that this event already exists and he have to update it
    # indeed, update and create method are the same in ExchangeCalendar (save())
    # these two parameters is the only way to let know exchange if it has to create
    # or update an event
    if c_event.exchange_id:
        x_item.item_id = c_event.exchange_id
        x_item.changekey = c_event.changekey
    # store the calsync id in the extern_id property, thanks exchange for this property
    x_item.extern_id = c_event.id
    x_item.subject = c_event.subject
    if c_event.is_all_day:
        # convert date into datetime
        start_dt = datetime.combine(c_event.start, datetime.min.time())
        end_dt = datetime.combine(c_event.end, datetime.min.time())
        x_item.is_all_day = True
    else:
        start_dt = c_event.start
        end_dt = c_event.end
        x_item.is_all_day = False
    x_item.start = tz.localize(EWSDateTime.from_datetime(start_dt.replace(tzinfo=None)))
    x_item.end = tz.localize(EWSDateTime.from_datetime(end_dt.replace(tzinfo=None)))
    return x_item