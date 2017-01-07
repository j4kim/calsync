from datetime import datetime

from exchangelib import DELEGATE, IMPERSONATION, Account, Credentials, \
    EWSDateTime, EWSTimeZone, Configuration, NTLM, CalendarItem

import sys
from calsync_calendar import CalsyncCalendar

class ExchangeCalendar(CalsyncCalendar):
    def __init__(self, name, server, username, address, pwd=None):
        CalsyncCalendar.__init__(self, name)

        if not pwd:
            # from getpass import getpass
            # pwd = getpass("Entrez votre mot de passe Exchange : ")
            pwd = input("Entrez votre mot de passe Exchange (attention, il va être affiché) : ")

        credentials = Credentials(username=username, password=pwd, is_service_account=False)
        try:
            self.account = Account(primary_smtp_address=address,
                                   config=Configuration(server=server,credentials=credentials,auth_type=NTLM),
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
        c_event["iCalUID"] = item.item_id
        c_event["summary"] = item.subject
        # les prop start et end des objets CalendarItem d'Exchange contiennent des EWSDateTime
        # C'est une spécialisation de la classe datetime de python donc c'est cool
        if item.is_all_day:
            c_event["start"] = item.start.date()
            c_event["end"] = item.end.date()
        else:
            c_event["start"] = item.start
            c_event["end"] = item.end
        # Exchange ne sauvegarde pas la date de dernière modification, juste une changekey, qui est
        # une string de 40 calaractères incrémentées à chaque modification
        c_event["updated"] = datetime.min # pour l'instant, on met la date de modification au 1er javier de l'an 1
        return c_event