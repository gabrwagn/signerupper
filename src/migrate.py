import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()

DB_FILE_PATH = ""


def connect():
    print(DB_FILE_PATH)
    return sqlite3.connect(DB_FILE_PATH)


if __name__ == "__main__":
    DB_FILE_PATH = os.getenv('DB_FILE_PATH')
    print('using database path: ', DB_FILE_PATH, '...')

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
                            locked integer DEFAULT 0
                         ); 
                         """

    cur.execute(create_event_query)
    c.commit()

    add_column_query = """
                       ALTER TABLE events 
                        ADD locked integer DEFAULT 0
                       """

    cur.execute(add_column_query)
    c.commit()

    c.close()


