import os

class CalsyncCalendar:
    """
    Abstract class representing a calendar
    Implementations are ExchangeCalendar, GoogleCalendar and IcsCalendar
    Not really abstract because we can instanciate a CalsyncCalendar,
    but it will be on a "bridge" purpose
    """

    def __init__(self, name):
        # dictrionnary containing CalsyncEvent objects referenced by calync_id as key
        self.events = {}
        # set containing calsync ids of events that have to be deleted in this calendar
        self.deleted = set()
        self.name = name

    def read_events(self):
        """Read all events in a calendar and then check if events have been deleted since last sync"""
        # will call the specific implementation in inherited classes
        self.read_events()
        # check and mark wich events have been deleted
        self.check_deleted()

    def join(self, other_cal):
        """
        Add all events of other_cal to self (only if events are not already in self or is a newer version)
        Also update the self.deleted set to repercute suppression from src cal to dest
        """
        self.deleted = self.deleted | other_cal.deleted # the | operator returns the union of sets
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

    def write_events(self):
        """
        Delete events that have been deleted in source,
        then write new or updated events.
        """
        for id in self.deleted:
            self.delete_event(id)
        for id, event in self.events.items():
            self.write_event(event)

    def write_event(self, event):
        """Create or update event if necessary"""
        if event.is_new:
            self.create_event(event)
            print('Event "{}" created'.format(event.subject))
        elif event.is_updated:
            self.update_event(event)
            print('Event "{}" updated'.format(event.subject))
        else:
            pass
            # print('Nothing to do with event "{}"'.format(event.subject))

    def override_subject(self, new_subject):
        """Replace all subjects in self events by the string given new_subject"""
        for id, event in self.events.items():
            event.subject = new_subject

    def check_deleted(self):
        """
        Compare the ids in self.events with those stored in the .cals/calname file.
        If an id is in the stored file but not in self, that means the event has been deleted,
        the id is inserted in the self.deleted set.
        Then, rewrite the file with current events ids.
        If the file does not exists, it means this is the first time we see this calendar,
        we just create the file with current ids
        """

        # create the .cals folder if it doesnt exists
        if not os.path.exists(".cals"):
            os.mkdir(".cals")

        # get all the ids of current events
        ids = set(self.events.keys())
        try:
            # open the file in read mode
            cal_file = open(".cals/"+self.name, 'r+')
            old_ids = cal_file.read().split()
            for id in old_ids:
                if id not in ids:
                    self.deleted.add(id)
                    # print("Event with id {} as been deleted".format(id))
            cal_file.close()
        except FileNotFoundError:
            # open() will fail if the file does not exists
            # it's ok, nothing to do
            pass

        # re-open the file in write mode
        cal_file_w = open(".cals/" + self.name, 'w')
        # write every ids separated with new lines
        [cal_file_w.write(id + '\n') for id in self.events.keys()]
        cal_file_w.close()

    def __repr__(self):
        """Return a pretty representation of the calendar's events"""
        s = "{:_^53}".format(" CALENDAR {} ".format(self.name))
        s += "\n{:^53}\n".format(self.__class__.__name__)
        s += "{:^25} + {:^25}".format(" date ", " subject ")
        if not self.events:
            s += '\nNo events found.'
        for id, event in self.events.items():
            s += "\n{:<25} : {}".format(str(event.start), event.subject)
        return s + '\n'


class VirtualCalendar(CalsyncCalendar):
    def __init__(self, name):
        CalsyncCalendar.__init__(self, name)

    def write_events(self):
        print("Warning : trying to write envents on a virtual Calendar")
