import os
import sqlite3

import discord
from discord.ext.commands import Bot
from dotenv import load_dotenv

import models.eventdb as db
from models.eventmodel import EventModel
from models.participantmodel import ParticipantModel

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = Bot(command_prefix='+')


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(name="playing with his robo-balls."))
    print("Logged in as " + client.user.name)

    channel_ids = [
        "645694916244013075",
        "636288994228830238"
    ]

    for channel_id in channel_ids:
        migrate_channel(channel_id)


def migrate_channel(channel_id):
    old_db_path = 'local/raids.db'
    c = sqlite3.connect(old_db_path)
    cur = c.cursor()

    get_old_event_query = """ SELECT * FROM info WHERE channel=? ORDER BY id DESC LIMIT 1 """

    cur.execute(get_old_event_query, (channel_id,))
    old_event_data = cur.fetchone()
    c.commit()
    c.close()

    raid_id = old_event_data[0]
    name = old_event_data[1]
    date = old_event_data[2]
    time = old_event_data[3]
    description = old_event_data[4]

    event = EventModel(client.user.id, name, date, time, description, channel_id)
    event.save()

    sql = """ SELECT * FROM players WHERE lockout=? AND channel=? """

    c = sqlite3.connect(old_db_path)
    cur = c.cursor()
    cur.execute(sql, (raid_id, channel_id))
    players_data = cur.fetchall()
    c.commit()
    c.close()

    for p in players_data:
        pname = p[1]
        pclass = p[2]
        prole = p[3]

        channel = client.get_channel(channel_id)
        member = discord.utils.get(channel.members, display_name=name)

        if member is not None:
            participant = ParticipantModel(member.id, pname, pclass, prole, channel_id)
            participant.save()


if __name__ == "__main__":
    db.init()
    client.run(token)