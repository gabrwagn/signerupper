import sqlite3
import os.path
from typing import Optional, List

DB_FILE_PATH = ""


def init():
    global DB_FILE_PATH
    DB_FILE_PATH = os.getenv('DB_FILE_PATH')
    print('using database path: ', DB_FILE_PATH, '...')
    print('making sure event table exists...')
    create_event_table()


def connect():
    return sqlite3.connect(DB_FILE_PATH)


def create_event_table():
    """
    Create the table which holds all created events
    """
    c = connect()
    cur = connect()

    create_event_query = """
                         CREATE TABLE IF NOT EXISTS events (
                            id integer PRIMARY KEY,
                            uid integer NOT NULL,
                            name text NOT NULL,
                            date text NOT NULL,
                            time text NOT NULL,
                            description text NOT NULL,
                            channel integer NOT NULL,
                            locked bool DEFAULT 0
                         ); 
                         """

    cur.execute(create_event_query)
    c.commit()
    c.close()


def get_event_id(channel_id):
    sql = """ SELECT id FROM events WHERE channel=? ORDER BY id DESC LIMIT 1 """

    c = connect()
    cur = c.cursor()
    cur.execute(sql, (channel_id,))
    event_data = cur.fetchone()

    c.commit()
    c.close()

    return event_data[0]


def get_event_participant_table_name(channel_id):
    return "participants_{}".format(get_event_id(channel_id))


def create_event_participants_table(channel_id):
    event_id = get_event_id(channel_id)

    c = connect()
    cur = c.cursor()

    # Usually don't want to format sql queries but the string does not originate from user input
    # It uses the id number of each event to create a unique table per event
    table_name = get_event_participant_table_name(channel_id)
    event_participant_table_query = f"""
                               CREATE TABLE IF NOT EXISTS {table_name} (
                                   id integer PRIMARY KEY,
                                   uid integer NOT NULL,
                                   name text NOT NULL,
                                   identifier text NOT NULL,
                                   role text NOT NULL,
                                   channel integer NOT NULL,
                                   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                   UNIQUE(uid, channel)
                               )
                               """
    event_participant_trigger_query = f"""CREATE TRIGGER {table_name}_trigger
                                              AFTER INSERT ON {table_name}
                                              BEGIN
                                                  UPDATE {table_name} 
                                                      SET timestamp = CURRENT_TIMESTAMP
                                                      WHERE id = new.id;
                                              END;
                                       """

    cur.execute(event_participant_table_query)
    cur.execute(event_participant_trigger_query)
    c.commit()
    c.close()


def insert_event(event):
    """
    Create a new event and with it a new table to hold all the events participants
    param channel_id: channel_id which this event was created in
    :param event: EventModel to put into database
    :return:
    """

    c = connect()
    cur = c.cursor()

    sql_info = """ INSERT INTO events(uid, name, date, time, description, channel)
                        VALUES(?,?,?,?,?,?) """

    cur.execute(sql_info, event.as_tuple())

    c.commit()
    c.close()

    # Create a new table for the event which we add each new signup to
    create_event_participants_table(event.channel_id)


def update_event(event):
    """
    Updates the latest event in the channel which the original event was created in
    param channel_id: channel_id which this event was created in
    :param event: EventModel to put into database
    :return:
    """
    event_id = get_event_id(event.channel_id)

    c = connect()
    cur = c.cursor()

    event_update_query = """ 
                         UPDATE events
                             SET name=?,
                                 date=?,
                                 time=?,
                                 description=?
                         WHERE id=?
                         """

    cur.execute(event_update_query, (event.name, event.date, event.time, event.description, event_id))

    c.commit()
    c.close()


def insert_participant(participant):
    """
    :param participant:
    :return:
    """

    c = connect()

    cur = c.cursor()

    table_name = get_event_participant_table_name(participant.channel_id)
    insertion_query = f""" 
                       INSERT OR IGNORE INTO {table_name} (uid,name,identifier,role,channel)
                             VALUES(?,?,?,?,?) 
                       """

    update_query = f""" 
                    UPDATE {table_name} 
                       SET role=? 
                       WHERE uid=? AND channel=? 
                    """

    cur.execute(insertion_query, participant.as_tuple())
    cur.execute(update_query, (participant.role, participant.uid, participant.channel_id))

    c.commit()
    c.close()


def get_event(channel_id):
    """
    :param channel_id:
    :return:
    """
    c = connect()
    cur = c.cursor()

    query = """ SELECT * FROM events WHERE channel=? ORDER BY id DESC LIMIT 1 """

    cur.execute(query, (channel_id,))
    event_data = cur.fetchone()
    c.commit()
    c.close()

    return event_data


def get_participant(channel_id, name):
    c = connect()
    cur = c.cursor()

    table_name = get_event_participant_table_name(channel_id)
    query = f""" 
            SELECT * FROM {table_name} 
                WHERE name=? AND channel=? 
            """

    cur.execute(query, (name, channel_id))
    participant_data = cur.fetchone()
    c.commit()
    c.close()

    return participant_data


def get_participants(channel_id):
    c = connect()
    cur = c.cursor()

    table_name = get_event_participant_table_name(channel_id)
    query = f""" 
            SELECT * FROM {table_name} 
                WHERE channel=? 
            """

    cur.execute(query, (channel_id,))
    participant_data_list = cur.fetchall()
    c.commit()
    c.close()

    return participant_data_list

