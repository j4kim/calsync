import os
import sys

from exchangelib import DELEGATE, Account, Credentials, \
    Configuration, NTLM, CalendarItem

from calsync_calendar import CalsyncCalendar
from exchange_event import ExchangeEvent, to_exchange
from simplecrypt import encrypt, decrypt
from getpass import getpass

class ExchangeCalendar(CalsyncCalendar):
    def __init__(self, name, server, username, address):
        CalsyncCalendar.__init__(self, name)

        try:
            with open(".exchange_pwd", 'rb') as pwd_file:
                pwd = decrypt('calsync', pwd_file.read()).decode("utf-8")
        except FileNotFoundError:
            pwd = getpass("Entrez votre mot de passe Exchange : ")
            with open(".exchange_pwd", 'wb') as pwd_file:
                pwd_file.write(encrypt("calsync", pwd))

        credentials = Credentials(username=username, password=pwd, is_service_account=False)
        try:
            self.account = Account(
                primary_smtp_address=address,
                config=Configuration(server=server,credentials=credentials,auth_type=NTLM),
                access_type=DELEGATE,
                locale="ch_fr")
        except FileNotFoundError:
            print("connexion au compte {} impossible".format(username), file=sys.stderr)
            os.remove(".exchange_pwd")
            sys.exit()
        super().read_events()

    def read_events(self):
        all_items = self.account.calendar.all()
        for item in all_items:
            x = ExchangeEvent(item)
            self.events[x.id] = x

    def create_event(self, event):
        to_exchange(event, self).save()

    def update_event(self, event):
        to_exchange(event, self).save()

    def delete_event(self, id):
        if id not in self.events:
            return
        to_exchange(self.events[id], self).delete()
        print("Event {} deleted".format(self.events[id].subject))

