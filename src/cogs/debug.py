import random

from discord.ext import commands

import models.eventdb as db
import views.eventview as view
from models.participantmodel import ParticipantModel
import settings
import utils.utils as utils


DEBUGGER = "Debugger"

player_names = [
    "//-+AssholeXXX"
    "derp - herp",
    "LOL/MAN"
    "Wankman",
    "Kattedragon",
    "Kattehesten",
    "Kattemanden",
    "Lololojika",
    "Swagman",
    "Smackfia",
    "Snaskfia",
    "Thunderfury",
    "Fagman",
    "Ragman",
    "Slackman",
    "Manman",
    "Tankmanny",
    "Wagfag",
    "Coolman",
    "Droolman",
    "Apeman",
    "Katteunicorn",
    "Woop",
    "Doop",
    "Loop",
    "Goop"
]

player_identifiers = {
    name: settings.IDENTIFIERS[random.randint(0, len(settings.IDENTIFIERS) - 1)] for name in player_names
}
player_roles = {
    name: settings.ROLES.ALL[random.randint(0, len(settings.ROLES.ALL) - 1)] for name in player_names
}

for name in player_roles:
    i = random.randint(0, 100)
    if i < 10:
        player_roles[name] = settings.ROLES.TANK
    if 10 < i < 15:
        player_roles[name] = settings.ROLES.CASTER
    if 15 < i < 20:
        player_roles[name] = settings.ROLES.PHYSICAL

player_ids = {name: random.randint(157794200182718464, 999794200182718464) for name in player_names}


class Debug(commands.Cog):
    """ Officer cog for routing officer commands. """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='spawn',
                      pass_context=True)
    @commands.has_role(DEBUGGER)
    async def spawn(self, ctx):
        for name in player_names:
            player_id = player_ids[name]
            identifier = player_identifiers[name]
            role = player_roles[name]
            participant = ParticipantModel(player_id, name, identifier, role, ctx.channel.id)
            db.insert_participant(participant)

        embed = view.create(ctx.channel.id, ctx.guild.emojis, self.bot.user.id)
        await utils.show_event(ctx.channel, self.bot, embed)
