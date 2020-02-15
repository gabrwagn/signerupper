import discord

import settings
from models.eventmodel import EventModel


def get_breakdown(group, check):
    group_breakdown = {}
    for participant in group:
        breakdown_param = check(participant)
        if participant.role not in group_breakdown.keys():
            group_breakdown[breakdown_param] = {"count": 0, "participants": []}
        group_breakdown[breakdown_param]["count"] += 1
        group_breakdown[breakdown_param]["participants"].append(participant.name)

    return group_breakdown


def add_breakdown_field(breakdown, embed):
    for key, value in breakdown.items():
        title = f'{key} - {value["count"]}'
        body = '\n'.join(value["participants"])
        embed.add_field(name=title, value=body, inline=False)


def create(channel_id):
    """
    Creates a nice summary of the event
    :param channel_id:
    :return:
    """
    event = EventModel.load(channel_id)
    participants = event.participants

    event_title = f"Summary for {event.name}:"

    participant_count = len(participants)
    active_participant_count = len(list(filter(lambda p: p.role in settings.ROLES.ACTIVE, participants)))
    backup_participant_count = len(list(filter(lambda p: p.role == settings.ROLES.BACKUP, participants)))

    event_subtext = '\n'.join([
        f"Time: {event.time}",
        f"Total players: {participant_count}",
        f"Total active players: {active_participant_count}",
        f"Total backup players: {backup_participant_count}",
    ])

    embed = discord.Embed(title=event_title, colour=discord.Colour(0x36393E), description=event_subtext)

    identifier_breakdown = get_breakdown(participants, lambda p: p.identifier)
    add_breakdown_field(identifier_breakdown, embed)

    active_role_breakdown = get_breakdown(participants, lambda p: p.role)
    add_breakdown_field(active_role_breakdown, embed)

    return embed


