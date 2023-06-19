import sqlite3
from sqlite3 import Error


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(
            "chatbot_database.db"
        )  # creates a SQLite database in memory
        return conn
    except Error as e:
        print(e)


def create_table(conn):
    try:
        sql_create_conversation_table = """ CREATE TABLE IF NOT EXISTS Conversations (
                                                id integer PRIMARY KEY,
                                                role text NOT NULL,
                                                message text NOT NULL
                                            ); """
        c = conn.cursor()
        c.execute(sql_create_conversation_table)
    except Error as e:
        print(e)


def insert_message(conn, role, message):
    try:
        sql_insert_message = """ INSERT INTO Conversations(role,message)
                                 VALUES(?,?) """
        cur = conn.cursor()
        cur.execute(sql_insert_message, (role, message))
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(e)
