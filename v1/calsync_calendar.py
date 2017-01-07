
class CalsyncCalendar:
    """Classe représentant un calendrier abstrait"""

    def __init__(self, name):
        # dictionnaire avec clé:uid d'un event et valeur:dictionnaire représentant un event
        self.events = {}
        self.name = name

    def __repr__(self):
        s = "{:_^53}".format(" CALENDAR {} ".format(self.name))
        s += "\n{:^53}".format(self.__class__.__name__)
        s += "\n{:^25} + {:^25}".format(" date ", " summary ")
        if not self.events:
            s += '\nNo events found.'
        for uid, event in self.events.items():
            s += "\n{:<25} : {}".format(str(event['start']), event["summary"])
            # s += " // {} / {} / {}".format(event["updated"],  event["iCalUID"], event.get("id","pas d'id"))
        return s

    def union(self, cal1, cal2):
        self.join(cal1)
        self.join(cal2)
        self.write_events()

    # add all events of other_cal to self (only if events are new or updated)
    def join(self, other_cal):
        for uid, event in other_cal.events.items():
            self.add(event)

    # idempotent addition
    def add(self, event):
        # reinitialize flags
        event["flags"] = set()
        uid = event["iCalUID"]
        # check if event does not already exists
        if uid not in self.events:
            # raise a flag to know that we have to create this event
            event['flags'].add("is_new")
            self.events[uid] = event

        # if the event exists, check if the last-update datetime has changed
        elif self.events[uid]["updated"] < event["updated"]:
            # if the event has been updated, replace it in the dictionnary
            # raise a flag for Google calendars update method instead of import
            event['flags'].add("has_been_updated")
            # bricolage pour permettre l'update par la google api qui a besoin de l'attribut id
            if "id" in self.events[uid]:
                event["id"] = self.events[uid]["id"]
            self.events[uid] = event
