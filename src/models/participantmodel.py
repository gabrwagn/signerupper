import models.eventdb as db


class ParticipantModel:
    def __init__(self, uid, name, identifier, role, channel_id):
        """
        Matches the database entry order
        :param uid:
        :param name:
        :param identifier:
        :param role:
        :param channel_id:
        """
        self.uid = uid
        self.name = name
        self.identifier = identifier
        self.role = role
        self.channel_id = channel_id
        self.timestamp = ""

    def __str__(self):
        return f"{self.uid} {self.name} {self.identifier} {self.role} {self.channel_id} {self.timestamp}"

    def as_tuple(self):
        """
        :return:  ParticipantModel as tuple (without uid)
        """
        return self.uid, self.name, self.identifier, self.role, self.channel_id

    def save(self):
        db.insert_participant(self)

    @classmethod
    def load(cls, channel_id, name):
        participant_data = db.get_participant(channel_id, name)
        if participant_data is not None:
            participant = ParticipantModel(*participant_data[1:-1])
            participant.timestamp = participant_data[-1]

            return participant

        return None
