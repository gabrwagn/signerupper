import os

import discord
from discord.ext.commands import Bot
from dotenv import load_dotenv

import models.eventdb as db
from cogs.admin import Admin
from cogs.user import User
from cogs.debug import Debug

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
debug = os.getenv('DEBUG')

client = Bot(command_prefix='+')

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
        print("Not allowed to delete that message")
    except discord.NotFound:
        pass
        # print("Could not find message to delete")
    except discord.HTTPException:
        print("Failed to delete message")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        print(str(error))
        return
    raise error


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(name="playing with his robo-balls."))
    print("Logged in as " + client.user.name)


if __name__ == "__main__":
    db.init()
    print('Starting up bot...')
    client.run(token)
