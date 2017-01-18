
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
    def add(self, src_event):
        # reinitialize flags
        src_event["flags"] = set()
        uid = src_event["iCalUID"]
        # check if event does not already exists
        if uid not in self.events:
            # raise a flag to know that we have to create this event
            src_event['flags'].add("is_new")
        else:
            # the event already exists in destination calendar
            dst_event = self.events[uid]
            # we don't know if src_event is different has dst_event (if it has been updated)
            if "updated" in src_event and "updated" in dst_event:
                # both events have the "udpated" key, so we can easily test which is the newer
                if dst_event["updated"] >= src_event["updated"]:
                    # src event has not been updated after dest event, do nothing
                    return
            else:
                # we don't know which one is the latest updated
                # for the moment, we will override de destination event in all cases
                pass
            # bricolage pour permettre l'update par la google api qui a besoin de l'attribut id
            if "id" in dst_event:
                src_event["id"] = dst_event["id"]

            # if we didnt return, raise the flag to let know dest calendar (self)
            # that it has to replace his version of the event
            src_event['flags'].add("has_been_updated")

        # add (or replace by) the source event in the destination calendar
        self.events[uid] = src_event
