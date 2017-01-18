from datetime import datetime, timezone

from exchangelib import DELEGATE, IMPERSONATION, Account, Credentials, \
    EWSDateTime, EWSTimeZone, Configuration, NTLM, CalendarItem

import sys
from calsync_calendar import CalsyncCalendar

class ExchangeCalendar(CalsyncCalendar):
    def __init__(self, name, server, username, address, pwd=None):
        CalsyncCalendar.__init__(self, name)

        try:
            with open(".exchange_pwd", encoding="utf-8") as pwd_file:
                pwd = pwd_file.read()
        except:
            pwd = None

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
            # print(item)
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
            # sauf que EWSDateTime n'est pas reconnu par google qui crée une erreur, il faut créer des datetime
            # j'ai pas trouvé le moyen python de caster une classe dérivée en classe parente, apparemment c'est
            # qqch qu'on ne devrait pas faire
            s = item.start
            e = item.end
            c_event["start"] = datetime(s.year, s.month, s.day, s.hour, s.minute, s.second, s.microsecond).replace(tzinfo=timezone.utc)
            c_event["end"] = datetime(e.year, e.month, e.day, e.hour, e.minute, e.second, e.microsecond).replace(tzinfo=timezone.utc)

        # Exchange ne sauvegarde pas la date de dernière modification, juste une changekey, qui est
        # une string de 40 calaractères incrémentées à chaque modification
        c_event["changekey"] = item.changekey
        # c_event["updated"] = datetime.min.replace(tzinfo=timezone.utc) # pour l'instant, on met la date de modification au 1er javier de l'an 1
        return c_event