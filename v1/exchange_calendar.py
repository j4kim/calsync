from datetime import datetime, timezone, date

from exchangelib import DELEGATE, IMPERSONATION, Account, Credentials, \
    EWSDateTime, EWSTimeZone, Configuration, NTLM, CalendarItem

import sys, uuid
from calsync_calendar import CalsyncCalendar

tz = EWSTimeZone.timezone('Europe/Copenhagen')

class ExchangeCalendar(CalsyncCalendar):
    def __init__(self, name, server, username, address, pwd=None):
        CalsyncCalendar.__init__(self, name)

        if not pwd:
            try:
                with open(".exchange_pwd", encoding="utf-8") as pwd_file:
                    pwd = pwd_file.read()
            except:
                # from getpass import getpass
                # pwd = getpass("Entrez votre mot de passe Exchange : ")
                pwd = input("Entrez votre mot de passe Exchange (attention, il va être affiché) : ")

        credentials = Credentials(username=username, password=pwd, is_service_account=False)
        try:
            self.account = Account(primary_smtp_address=address,
                                   config=Configuration(
                                       server=server,credentials=credentials,auth_type=NTLM
                                   ),
                                   access_type=DELEGATE,
                                   locale="ch_fr")
        except:
            print("Erreur de connexion au compte {}".format(username), file=sys.stderr)
            return
        self.read_events()

    def read_events(self):
        all_items = self.account.calendar.all()
        for item in all_items:
            c_event = ExchangeCalendar.to_calsync_event(item)
            self.events[c_event["iCalUID"]] = c_event

    @staticmethod
    def to_calsync_event(item):
        c_event = {}
        # if item.extern_id is None:
        #     item.extern_id = "calsync_exchange_" + str(uuid.uuid1())
        #     item.save()
        #     print("--> first time calsync sees event {}, generated id {}".format(item.subject, item.extern_id))
        # c_event["iCalUID"] = item.extern_id
        # c_event["exchange_id"] = item.item_id
        if item.extern_id is not None:
            c_event["iCalUID"] = item.extern_id
        else:
            c_event["iCalUID"] = item.item_id
        c_event["exchange_id"] = item.item_id
        c_event["changekey"] = item.changekey

        c_event["summary"] = item.subject
        # les prop start et end des objets CalendarItem d'Exchange contiennent des EWSDateTime
        # C'est une spécialisation de la classe datetime de python donc c'est cool
        if item.is_all_day:
            c_event["start"] = item.start.date()
            c_event["end"] = item.end.date()
        else:
            # sauf que EWSDateTime n'est pas reconnu par google qui crée une erreur, il faut créer des datetime
            # j'ai pas trouvé le moyen python de caster une classe dérivée en classe parente, apparemment c'est
            # qqch qu'on ne devrait pas faire
            s = item.start
            e = item.end
            c_event["start"] = datetime(s.year, s.month, s.day, s.hour, s.minute, s.second, s.microsecond).replace(tzinfo=timezone.utc)
            c_event["end"] = datetime(e.year, e.month, e.day, e.hour, e.minute, e.second, e.microsecond).replace(tzinfo=timezone.utc)
        return c_event

    def write_events(self):
        for uid, event in self.events.items():
            self.write_event(event)

    def write_event(self, event):
        if 'flags' in event and event["flags"]:
            # transforme le calsync Event en exchange Event
            x_event = self.to_exchange_event(event)
            if "is_new" in event["flags"]:
                x_event.save()
                print('Exchange event "{}" created'.format(event["summary"]))
            elif "has_been_updated" in event["flags"]:
                # cela aurait réglé tous mes soucis
                # malheureusement, ça ne marche pas, on ne peut pas filtrer les items par extern_id
                # src_item = self.account.calendar.get(extern_id = event["iCalUID"])
                # x_event.item_id = src_item.item_id
                x_event.save()
                print('Exchange event "{}" updated'.format(event["summary"]))
                # print('Exchange event "{}" already exists, calsync is unable to update it'.format(event["summary"]))
        else:
            # if no flags are raised, there is nothing to do
            print('nothing to do with Exchange event "{}"'.format(event["summary"]))


    def to_exchange_event(self, c_event):
        item = CalendarItem(folder = self.account.calendar)
        item.account = self.account
        if "exchange_id" in c_event:
            item.item_id = c_event["exchange_id"]
            item.changekey = c_event["changekey"]
        item.extern_id = c_event["iCalUID"]
        item.subject = c_event["summary"]
        item.is_all_day = False
        if isinstance(c_event["start"], date):
            # convert date into datetime
            c_event["start"] = datetime.combine(c_event["start"], datetime.min.time())
            c_event["end"] = datetime.combine(c_event["end"], datetime.min.time())
            item.is_all_day = True
        item.start=tz.localize(EWSDateTime.from_datetime(c_event["start"]))
        item.end=tz.localize(EWSDateTime.from_datetime(c_event["end"]))
        return item
