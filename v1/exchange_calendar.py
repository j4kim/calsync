import sys

from exchangelib import DELEGATE, Account, Credentials, \
    Configuration, NTLM

from calsync_calendar import CalsyncCalendar
from exchange_event import ExchangeEvent, to_exchange

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
            print("connexion au compte {} impossible".format(username), file=sys.stderr)
            sys.exit()
        self.read_events()

    def read_events(self):
        all_items = self.account.calendar.all()
        for item in all_items:
            x = ExchangeEvent(item)
            self.events[x.id] = x

    def create_event(self, event):
        to_exchange(event, self).save()

    def update_event(self, event):
        to_exchange(event, self).save()
