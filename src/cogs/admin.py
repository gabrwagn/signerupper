import discord
from discord.ext import commands

from models.eventmodel import EventModel
from models.participantmodel import ParticipantModel
from utils.date import is_valid_date_time, is_date_time_expired, try_parse_day
from utils.eventaspectparser import EventAspectParser
import utils.errors as errors
import utils.utils as utils
import views.eventview as view
import views.summaryview as summary
import settings


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='event',
                      description='Create a new event by providing a name, date and time separated by spaces.'
                                  'Optionally add an event description, example: \n'
                                  '+event "Onyxia" 2020-10-11 19:00 "Clearing up whatever is left"\n'
                                  'The date can also be a weekday (assumed to be the next upcoming date of that day):\n'
                                  '+event "Molten Core" thursday 19:00',
                      brief='Create a new raid event.',
                      aliases=['addevent'],
                      pass_context=True)
    @commands.has_role(settings.ROLES.ADMIN)
    @commands.guild_only()
    async def create_event(self, ctx: commands.Context, name, date, time, description=""):

        date = try_parse_day(date)
        if not is_valid_date_time(date, time):
            await ctx.author.send(errors.INVALID_DATE.format(date, time))
            return

        if is_date_time_expired(date, time):
            await ctx.author.send(errors.EXPIRED_DATE.format(date, time))
            return

        event = EventModel(self.bot.user.id, name, date, time, description, ctx.channel.id, 0)
        event.save()

        embed = view.create(ctx.channel.id, ctx.guild.emojis, self.bot.user.id)
        await utils.show_event(channel=ctx.channel, client=self.bot, embed=embed, new_event=True)
        await utils.send_announcement(ctx, settings.MESSAGE.NEW_EVENT.format(event.name, event.date, event.time,
                                                                             ctx.channel.mention))
        utils.log(ctx.author.display_name, "created event", event.name, "...")

    @commands.command(name='place',
                      description='Place a member into the event, optionally a specific role can be set.'
                                  'If the member has already signed they will just be moved to the role provided,'
                                  'if they have not yet signed they will be assigned their default role or the'
                                  'provided role in the command.',
                      brief='Place a member into a specific role',
                      aliases=[],
                      pass_context=True)
    @commands.has_role(settings.ROLES.ADMIN)
    @commands.guild_only()
    async def place(self, ctx: commands.Context, name, role=""):
        name = utils.prune_participant_name(name)
        role = role.title()

        if role and role not in settings.ROLES.ALL:
            await ctx.author.send(errors.NONEXISTENT_ROLE)
            return

        event = EventModel.load(ctx.channel.id)
        if event is None:
            await ctx.author.send(errors.NONEXISTENT_EVENT)
            return

        participant = ParticipantModel.load(ctx.channel.id, name)

        # Participant is not currently part of the event, try to find the member in the server
        user = discord.utils.find(lambda m: utils.fuzzy_string_match(m.display_name, name), ctx.guild.members)
        if user is None:
            await ctx.author.send(errors.NONEXISTENT_MEMBER)

        identifier = utils.extract_identifier(user)
        if identifier is None:
            await user.send(errors.NO_VALID_ROLE)
            return

        # If a role was not provided find the default one for the member
        if not role:
            role = utils.extract_role(user, identifier)

        if participant is None:
            participant = ParticipantModel(user.id, name, identifier, role, ctx.channel.id)
        else:
            current_role = participant.role
            if current_role == role:
                return
            participant.role = role.title()

        participant.save()

        embed = view.create(ctx.channel.id, ctx.guild.emojis, self.bot.user.id)
        await utils.show_event(channel=ctx.channel, client=self.bot, embed=embed)
        await user.send(settings.MESSAGE.PLACEMENT.format(role, event.name, event.date, ctx.channel.mention))
        utils.log(ctx.author.display_name, "placed player", name, "...")

    @commands.command(name='edit',
                      description='Edit one or more aspects of an event: name, date, time or description (descr), '
                                  'example: \n +edit "name=Molten Core + Onyxia" \n'
                                  'multiple aspects ca be changed at the same time separated by space:\n'
                                  '+edit "time=18:00" "descr=Rescheduled because we almost cleared"',
                      brief='Edit aspects of an event',
                      pass_context=True)
    @commands.has_role(settings.ROLES.ADMIN)
    @commands.guild_only()
    async def edit(self, ctx: commands.Context, *raw_aspects):
        event = EventModel.load(ctx.channel.id)
        if event is None:
            await ctx.author.send(errors.NONEXISTENT_EVENT)
            return

        parsed_aspect_dict, invalids = EventAspectParser.parse(raw_aspects)
        for name, value in parsed_aspect_dict.items():
            event.set_attribute(name, value)

        if len(invalids) > 0:
            await ctx.author.send(errors.INVALID_ASPECTS + '\n' + '\n'.join(invalids))

        if is_date_time_expired(event.date, event.time):
            await ctx.author.send(errors.EXPIRED_DATE.format(event.date, event.time))
            return

        event.save(append=True)

        embed = view.create(ctx.channel.id, ctx.guild.emojis, self.bot.user.id)
        await utils.show_event(channel=ctx.channel, client=self.bot, embed=embed, new_event=False)
        utils.log(ctx.author.display_name, "edited event", event.name, "...")
        # TODO: Announce event edit

    @commands.command(name='summary', description='Summarize event', brief='Summarize event', pass_context=True)
    @commands.has_role(settings.ROLES.ADMIN)
    @commands.guild_only()
    async def summary(self, ctx: commands.Context):
        event = EventModel.load(ctx.channel.id)
        if event is None:
            await ctx.author.send(errors.NONEXISTENT_EVENT)
            return

        embed = summary.create(ctx.channel.id)
        await ctx.author.send(embed=embed)

    @commands.command(name='remind',
                      description='Remind all actively signed participants about this event',
                      brief='Ping players who signed.',
                      pass_context=True)
    @commands.has_role(settings.ROLES.ADMIN)
    @commands.guild_only()
    async def remind(self, ctx: commands.Context):
        event = EventModel.load(ctx.channel.id)
        if event is None:
            await ctx.author.send(errors.NONEXISTENT_EVENT)
            return

        participants = event.participants
        for participant in participants:
            member = discord.utils.find(lambda m: m.display_name == participant.name, ctx.guild.members)
            if member is not None:
                await member.send(settings.MESSAGE.REMINDER.format(event.name, event.date, event.time))

    @commands.command(name='lock',
                      description='Lock an event, forcing new sign-ups to be backup',
                      brief='Lock event',
                      pass_context=True)
    @commands.has_role(settings.ROLES.ADMIN)
    @commands.guild_only()
    async def lock(self, ctx: commands.Context):
        event = EventModel.load(ctx.channel.id)
        if event is None:
            await ctx.author.send(errors.NONEXISTENT_EVENT)
            return

        if not event.is_locked():
            event.lock()
            event.save(append=True)

            embed = view.create(ctx.channel.id, ctx.guild.emojis, self.bot.user.id)
            await utils.show_event(channel=ctx.channel, client=self.bot, embed=embed, new_event=False)

    @commands.command(name='unlock',
                      description='Unlock an event, forcing new sign-ups to be backup',
                      brief='Unlock event',
                      pass_context=True)
    @commands.has_role(settings.ROLES.ADMIN)
    @commands.guild_only()
    async def unlock(self, ctx: commands.Context):
        event = EventModel.load(ctx.channel.id)
        if event is None:
            await ctx.author.send(errors.NONEXISTENT_EVENT)
            return

        if event.is_locked():
            event.unlock()
            event.save(append=True)
            embed = view.create(ctx.channel.id, ctx.guild.emojis, self.bot.user.id)
            await utils.show_event(channel=ctx.channel, client=self.bot, embed=embed, new_event=False)

    @commands.command(name='refresh', description='Refresh the event', brief='Refresh the event', pass_context=True)
    @commands.has_role(settings.ROLES.ADMIN)
    @commands.guild_only()
    async def refresh(self, ctx: commands.Context):
        embed = view.create(ctx.channel.id, ctx.guild.emojis, self.bot.user.id)
        await utils.show_event(channel=ctx.channel, client=self.bot, embed=embed, new_event=False)

    @commands.command(name='clear', description='Remove ALL messages', brief='Clear channel', pass_context=True)
    @commands.has_role(settings.ROLES.ADMIN)
    @commands.guild_only()
    async def clear(self, ctx: commands.Context):
        await ctx.channel.purge(check=lambda m: m.id != ctx.message.id)  # The message will be deleted in on_message

    @commands.command(name='echo', description='Bot echoes your message', brief='Echo your message', pass_context=True)
    @commands.has_role(settings.ROLES.ADMIN)
    @commands.guild_only()
    async def echo(self, ctx: commands.Context, message):
        await ctx.channel.send(message)
