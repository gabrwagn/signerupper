from models.participantmodel import ParticipantModel
import models.eventdb as db


class EventModel:
    def __init__(self, uid, name, date, time, description, channel_id, locked):
        """
        Matches the database entry order
        :param name:
        :param date:
        :param time:
        :param description:
        :param channel_id:
        """
        self.id = 0
        self.uid = uid
        self.name = name
        self.date = date
        self.time = time
        self.description = description
        self.channel_id = channel_id
        self.participants = []
        self.locked = locked

        self._loaded = False

    def as_tuple(self):
        """
        :return:  EventModel as tuple (without uid)
        """
        return self.uid, self.name, self.date, self.time, self.description, self.channel_id, self.locked

    def set_attribute(self, name, value):
        """
        Somewhat ugly way to have easy access by string to the attributes
        Should probably throw if the attribute does not exist
        :param name:
        :param value:
        :return:
        """
        if hasattr(self, name):
            setattr(self, name, value)

    def save(self, append=False):
        """
        Writes this event to the database
        :param append: If append is true this will edit the current event instead of overwriting it with a new event
        :return:
        """

        if self._loaded or append:
            db.update_event(self)
        else:
            db.insert_event(self)

    @classmethod
    def load(cls, channel_id):
        """
        Loads an event from database if it exists.
        It also loads all participants of the event into its participants list.
        :param channel_id:
        :return:
        """
        event_data = db.get_event(channel_id)
        event = None
        if event_data is not None:
            event = EventModel(*event_data[1:])
            event._loaded = True
            participant_data_list = db.get_participants(channel_id)
            if participant_data_list is not None:
                participants = []
                for participant_data in participant_data_list:
                    participant = ParticipantModel(*participant_data[1:-1])
                    participant.timestamp = participant_data[-1]
                    participants.append(participant)

                event.participants = participants

        return event

    def lock(self):
        self.locked = 1

    def is_locked(self):
        return self.locked == 1
