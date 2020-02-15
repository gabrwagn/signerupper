import discord
from discord import Member
from discord.ext import commands

from models.eventmodel import EventModel
from models.participantmodel import ParticipantModel
import utils.errors as errors
import utils.utils as utils
import utils.date as date
import views.eventview as view
import settings


def has_valid_role():
    async def predicate(ctx):
        if ctx.author is Member:
            for role in ctx.author.roles:
                if role.name.title() in settings.VALID_USER_ROLES:
                    return True
        return False

    return commands.check(predicate)


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='sign',
                      description="Sign up for an event. Can be used if you have previously declined.",
                      brief="Sign up to an event.",
                      aliases=['signup'],
                      pass_context=True)
    @has_valid_role()
    async def signup(self, ctx: commands.Context):
        identifier = utils.extract_identifier(ctx.author)
        if identifier is None:
            await ctx.author.send(errors.NO_VALID_ROLE)
            return

        role = utils.extract_role(ctx.author, identifier)
        await self.handle_event_response(ctx.author, ctx.channel, role)

    @commands.command(name='decline',
                      description="Decline an event. Can be used if you have previously signed.",
                      brief="Decline an event.",
                      aliases=[''],
                      pass_context=True)
    @has_valid_role()
    async def decline(self, ctx: commands.Context):
        await self.handle_event_response(ctx.author, ctx.channel, settings.ROLES.DECLINED)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = self.bot.get_channel(payload.channel_id)
        emoji = payload.emoji

        message = None
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            print("Message was not found...")
        except discord.Forbidden:
            print("Access to message was Forbidden...")
        except discord.HTTPException:
            print("Retrieving message failed...")

        if all(var is not None for var in [guild, message, channel]):
            member = guild.get_member(payload.user_id)
            if member is not None and member != self.bot.user:
                if message.author == self.bot.user:
                    await self.handle_event_reaction(member, channel, emoji)

    async def handle_event_reaction(self, user, channel, emoji):
        identifier = utils.extract_identifier(user)

        if str(emoji) == settings.SIGNUP_REACTION:
            role = utils.extract_role(user, identifier)
            await self.handle_event_response(user, channel, role)
        elif str(emoji) == settings.DECLINE_REACTION:
            role = settings.ROLES.DECLINED
            await self.handle_event_response(user, channel, role)
        else:
            return

    async def handle_event_response(self, user, channel, role):
        event = EventModel.load(channel.id)

        if event is None:
            await user.send(errors.NONEXISTENT_EVENT)
            return False

        if date.is_date_time_expired(event.date, event.time):
            await user.send(errors.EXPIRED_EVENT)
            return False

        identifier = utils.extract_identifier(user)
        if identifier is None:
            await user.send(errors.NO_VALID_ROLE)
            print("participant tried to sign up without a role.")
            return

        name = user.display_name.title()
        name = utils.prune_participant_name(name)

        print(name)
        if not name:  # Empty string
            await user.send(errors.INVALID_NAME)
            print("participant tried to sign up with a shitty name.")
            return

        current_role = ""
        participant = ParticipantModel.load(channel.id, name)
        if participant is not None:
            current_role = participant.role

        if current_role == settings.ROLES.BACKUP:
            await user.send(errors.BACKUP_SIGN)
            print("participant tried to sign up but was already backup.")
            return

        if current_role == role:
            return

        participant = ParticipantModel(user.id, name, identifier, role, channel.id)
        participant.save()

        embed = view.create(channel.id, user.guild.emojis, self.bot.user.id)
        await utils.show_event(channel=channel, client=self.bot, embed=embed)

