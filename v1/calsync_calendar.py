import json

class CalsyncCalendar:
    """Classe représentant un calendrier abstrait"""

    def __init__(self, name):
        # dictionnaire avec clé:calsync_id d'un event et valeur:objet CalsyncEvent
        self.events = {}
        self.deleted = set()
        self.name = name

    def read_events(self):
        self.read_events()
        self.check_deleted()

    def __repr__(self):
        s = "{:_^53}".format(" CALENDAR {} ".format(self.name))
        s += "\n{:^53}\n".format(self.__class__.__name__)
        s += "{:^25} + {:^25}".format(" date ", " subject ")
        if not self.events:
            s += '\nNo events found.'
        for id, event in self.events.items():
            s += "\n{:<25} : {}".format(str(event.start), event.subject)
        return s + '\n'

    def union(self, cal1, cal2):
        self.join(cal1)
        self.join(cal2)
        self.write_events()

    # add all events of other_cal to self (only if events are new or updated)
    def join(self, other_cal):
        self.deleted = self.deleted | other_cal.deleted
        for id, event in other_cal.events.items():
            self.add(event)

    def add(self, src_event):
        """idempotent addition: add or replace src_event in self, which is the destination calendar"""

        # first, reinitialize flags, in case this event has multiple destinations
        src_event.is_new = False
        src_event.is_updated = False

        id = src_event.id

        # check if event does not already exists in destination calendar
        if id not in self.events:
            # raise a flag to know that we have to create this event
            src_event.is_new = True
        else:
            # the event already exists in destination calendar
            dst_event = self.events[src_event.id]
            # we don't know yet which version of the event we should keep
            if dst_event.updated and src_event.updated:
                # both events have the "udpated" attribute, so we can easily test which is the newer
                if dst_event.updated >= src_event.updated:
                    # src event has not been updated after dest event, do nothing
                    return
            else:
                # we don't know which one is the latest updated
                # for the moment, we will override the destination event in all cases
                pass

            if dst_event.google_id:
                src_event.google_id = dst_event.google_id
            if dst_event.exchange_id:
                src_event.exchange_id = dst_event.exchange_id
                src_event.changekey = dst_event.changekey

            # if we didnt return, raise the flag to let know dest calendar (self)
            # that it has to replace his version of the event
            src_event.is_updated = True

        # add (or replace by) the source event in the destination calendar
        self.events[id] = src_event

    # insert or update events
    def write_events(self):
        for api_id in self.deleted:
            self.delete_event(api_id)
        for id, event in self.events.items():
            self.write_event(event)

    def write_event(self, event):
        if event.is_new:
            self.create_event(event)
            print('Event "{}" created'.format(event.subject))
        elif event.is_updated:
            self.update_event(event)
            print('Event "{}" updated'.format(event.subject))
        else:
            print('Nothing to do with event "{}"'.format(event.subject))

    def override_subject(self, new_subject):
        for id, event in self.events.items():
            event.subject = new_subject

    def check_deleted(self):
        api_ids = {e.api_id for i,e in self.events.items()}

        try:
            # open the file in read mode
            cal_file = open(".cals/"+self.name, 'r+')
            old_ids = cal_file.read().split()
            for id in old_ids:
                if id not in api_ids:
                    self.deleted.add(id)
                    print("Event {} as been deleted".format(id))
            cal_file.close()
        except FileNotFoundError:
            # open() will fail if the file does not exists
            # it's ok, nothing to do
            pass

        # re-open the file in write mode
        cal_file_w = open(".cals/" + self.name, 'w')
        [cal_file_w.write(e.google_id + '\n') for id, e in self.events.items()]
        cal_file_w.close()