import os
import sys

from exchangelib import DELEGATE, Account, Credentials, \
    Configuration, NTLM

from calsync_calendar import CalsyncCalendar
from exchange_event import ExchangeEvent, to_exchange
from simplecrypt import encrypt, decrypt
from getpass import getpass

class ExchangeCalendar(CalsyncCalendar):
    """Implementation of CalsyncCalendar that connects to Exchange and can manage events"""

    def __init__(self, name, server, username, address):
        """Initialize an Exchange calendar and try to connect to the Exchange account according to the
        arguments given. The password will be prompted the first time, then it will be encrypted
        and stored in a ".exchange_pwd" file"""
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
        except:
            print("connexion au compte {} impossible".format(username), file=sys.stderr)
            os.remove(".exchange_pwd")
            sys.exit()
        # calls the calsync_calendar.read_events method
        super().read_events()

    def read_events(self):
        """Read all items from the Exchange account's calendar folder
        The events read are CalendarItem objects, we convert them to ExchangeEvents objects,
        which are CalsyncEvent objects"""
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
        try:
            to_exchange(self.events[id], self).delete()
            print("Event {} deleted".format(self.events[id].subject))
        except:pass

