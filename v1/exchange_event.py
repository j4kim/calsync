from datetime import datetime

from exchangelib import CalendarItem, EWSDateTime, EWSTimeZone

from calsync_event import CalsyncEvent

tz = EWSTimeZone.timezone('Europe/Copenhagen')

class ExchangeEvent(CalsyncEvent):
    def __init__(self, x_item):
        CalsyncEvent.__init__(self)

        if x_item.extern_id is not None:
            self.id = x_item.extern_id
        else:
            self.id = x_item.item_id

        self.api_id = self.exchange_id = x_item.item_id
        self.changekey = x_item.changekey
        self.subject = x_item.subject

        # les prop start et end des objets CalendarItem d'Exchange contiennent des EWSDateTime
        # C'est une spécialisation de la classe datetime de python donc c'est cool
        if x_item.is_all_day:
            self.start = x_item.start.date()
            self.end = x_item.end.date()
            self.is_all_day = True
        else:
            # sauf que EWSDateTime n'est pas reconnu par google qui crée une erreur, il faut créer des datetime
            # j'ai pas trouvé le moyen python de caster une classe dérivée en classe parente, apparemment c'est
            # qqch qu'on ne devrait pas faire
            s = x_item.start
            e = x_item.end
            self.start = datetime(s.year, s.month, s.day, s.hour, s.minute, s.second, s.microsecond)
            self.end = datetime(e.year, e.month, e.day, e.hour, e.minute, e.second, e.microsecond)
            self.is_all_day = False


def to_exchange(c_event, x_calendar):
    x_item = CalendarItem(folder = x_calendar.account.calendar)
    x_item.account = x_calendar.account
    if c_event.exchange_id:
        x_item.item_id = c_event.exchange_id
        x_item.changekey = c_event.changekey
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