import models.eventdb as db


class EventModel:
    def __init__(self, uid, name, date, time, description, channel_id):
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

    def as_tuple(self):
        """
        :return:  EventModel as tuple (without uid)
        """
        return self.uid, self.name, self.date, self.time, self.description, self.channel_id

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
        if append:
            db.update_event(self)
        else:
            db.insert_event(self)

    @classmethod
    def load(cls, channel_id):
        return db.get_event(channel_id)