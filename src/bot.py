import os

import discord
from discord.ext.commands import Bot
from dotenv import load_dotenv

import models.eventdb as db
from cogs.admin import Admin
from cogs.user import User
from cogs.debug import Debug
from utils import utils

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
debug = os.getenv('DEBUG')

intents = discord.Intents.default()
intents.members = True

client = Bot(command_prefix='+', intents=intents)

client.add_cog(User(client))
client.add_cog(Admin(client))
if debug == 'TRUE':
    client.add_cog(Debug(client))


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    await client.process_commands(message)

    try:
        await message.delete()
    except discord.Forbidden:
        utils.log("Not allowed to delete message...")
    except discord.NotFound:
        pass
        # print("Could not find message to delete")
    except discord.HTTPException:
        utils.log("Failed to delete message in channel")


@client.event
async def on_command_error(ctx, error):
    error_str = str(error)
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.author.send(error_str)
        utils.log("Command error:", error_str)
        return
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.author.send(error_str)
        utils.log("Command error:", error_str)
        return
    if isinstance(error, discord.ext.commands.errors.CheckFailure):
        await ctx.author.send("That command can't be used in a DM, or you don't have the correct role for that command!")
        utils.log("Command error:", error_str)
        return
    if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        await ctx.author.send("The bot does not have the correct rights to run that command.")
        utils.log("Command error:", error_str)
        return

    utils.log("Command error:", error_str)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(name="playing with his robo-balls."))
    utils.log("Logged in as " + client.user.name)


if __name__ == "__main__":
    db.init()
    utils.log('Starting up bot...')
    client.run(token)
