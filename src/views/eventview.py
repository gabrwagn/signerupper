import discord

import utils.date as date
import settings
from models.eventmodel import EventModel
from utils import utils

zero_width_space = '\u200b'
zero_width_line_break = '\u200b\n'
zero_width_double_line_break = '\n\u200b\n'


def add_info_fields(embed, event, active_participant_count, backup_participant_count):
    signup_count_str = f" {active_participant_count}/{settings.DEFAULT_CAP_PARTICIPANTS}  {zero_width_space}" \
                               f" ({backup_participant_count}){zero_width_line_break} "
    embed.add_field(name=zero_width_space, value=f":crossed_swords: {signup_count_str} {zero_width_line_break}")
    embed.add_field(name=zero_width_space, value=f":calendar: {event.date} {zero_width_line_break}")
    embed.add_field(name=zero_width_space, value=f":clock1: {event.time} {zero_width_line_break}")


def create_participant_role_dict(decorators, participants):
    """
    Creates a dictionary where each key is the possible roles with lists of each player that has that role as values
    :param decorators:
    :param participants:
    :return:
    """
    role_dict = {}

    for role in settings.ROLES.ALL:
        role_dict[role] = []

    ranked_participants_dict = create_ranked_participant_dict(participants)
    participants.sort(key=lambda p: p.identifier, reverse=True)
    for participant in participants:
        rank = ranked_participants_dict[participant]
        decorator = discord.utils.get(decorators, name=participant.identifier.lower())
        participant_name = utils.prune_participant_name(participant.name)
        participant_entry = f"{decorator}  {participant_name[0:settings.PARTICIPANT_MAX_NAME_LENGTH]}  {rank}"
        role_dict[participant.role].append(participant_entry)

    return role_dict


def create_ranked_participant_dict(participants):
    """
    Creates a dictionary which assigns each participant a rank (formatted string) which is the order
    in which they signed up for an active role
    :param participants:
    :return:
    """
    participants.sort(key=lambda p: date.parse_date_time_str(p.timestamp))

    ranked_participant_dict = {}

    rank = 1
    for participant in participants:
        rank_str = ""
        if participant.role in settings.ROLES.ACTIVE:
            rank_str = f" `{rank}`"
            rank += 1
        ranked_participant_dict[participant] = rank_str

    return ranked_participant_dict


def create(channel_id, decorators, uid):
    """
    Creates a rich embed for the event in this channel and fills it with all participants
    :param uid:
    :param decorators:
    :param channel_id:
    :return:
    """
    event = EventModel.load(channel_id)

    if event is None:
        return discord.Embed(title="Error!", colour=discord.Colour(0x36393E))

    active_participant_count = len(list(filter(lambda p: p.role in settings.ROLES.ACTIVE, event.participants)))
    backup_participant_count = len(list(filter(lambda p: p.role == settings.ROLES.BACKUP, event.participants)))

    embed_fields = []

    participant_role_dict = create_participant_role_dict(decorators, event.participants)
    for role, participants in participant_role_dict.items():
        name = f"**[{len(participants)}]   __{role}__**"
        participants_str = '\n'.join(participants)  # turn the list into a string with linebreaks
        value = f"{zero_width_line_break} {participants_str} {zero_width_double_line_break}"

        embed_fields.append({'name': name, 'value': value})

    event_title = f"__**{event.name}**__"
    event_subtext = zero_width_double_line_break.join([event.description, settings.INSTRUCTIONS])
    embed = discord.Embed(title=event_title, colour=discord.Colour(0x36393E), description=event_subtext)
    add_info_fields(embed, event, active_participant_count, backup_participant_count)

    for embed_field in embed_fields:
        embed.add_field(name=embed_field['name'], value=embed_field['value'], inline=True)
    embed.set_footer(text=uid)

    return embed
