import discord
from discord import Embed

import settings


def prune_participant_name(name):
    name = name.split(' ')[0]
    name = name.split('/')[0]
    name = name.split('\\')[0]
    name = name.split('-')[0]
    name = name.split('(')[0]
    name = name.split(')')[0]
    name = name.split('+')[0]
    name = name.split('&')[0]
    name = name.title()

    return name


def fuzzy_string_match(first, second):
    if len(first) > 3:
        return second.lower() in first.lower()
    else:
        return first.lower() == second.lower()


async def send_announcement(ctx, announcement):
    for channel in ctx.guild.channels:
        if channel.name.lower() == settings.ANNOUNCEMENT_CHANNEL_NAME.lower():
            await channel.send(announcement)
            break


def extract_identifier(member):
    for role in member.roles:
        if role.name.title() in settings.IDENTIFIERS:
            return role.name.title()
    return None


def extract_role(member, identifier):
    for role in member.roles:
        if role.name.title() in settings.ROLES.ALL:
            return role.name.title()
    return settings.ROLES.from_identifier_default(identifier.title())


async def show_event(channel, client, embed, new_event=False):
    def is_event_message(m):
        # Look for a message that has an embed with a footer that contains the id of the bot
        if len(m.embeds) > 0:
            footer = m.embeds[0].footer
            return False if footer is Embed.Empty else str(client.user.id) == m.embeds[0].footer.text
        return False

    # Check if the bot has an event message in this channel already
    event_message = await channel.history().find(is_event_message)
    await channel.purge(check=lambda m: not is_event_message(m))

    if event_message is None:
        event_message = await channel.send(embed=embed)
        new_event = True
    else:
        await event_message.edit(embed=embed)

    if new_event:
        await event_message.clear_reactions()
        await event_message.add_reaction(emoji=settings.SIGNUP_REACTION)
        await event_message.add_reaction(emoji=settings.DECLINE_REACTION)

