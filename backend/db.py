import sqlite3
from sqlite3 import Error
from flask import current_app, g
import os

def get_db():
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
        g.db = db
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("chatbot_database.db")
        return conn
    except Error as e:
        print(e)


def create_conversation_table(conn):
    try:
        sql_create_conversation_table = """CREATE TABLE IF NOT EXISTS Conversations (
                                            id INTEGER PRIMARY KEY,
                                            user_id INTEGER NOT NULL,
                                            role TEXT NOT NULL,
                                            message TEXT NOT NULL,
                                            FOREIGN KEY (user_id) REFERENCES Users (id)
                                        );"""
        c = conn.cursor()
        c.execute(sql_create_conversation_table)
    except Error as e:
        print(e)


def create_users_table(conn):
    try:
        sql_create_users_table = """CREATE TABLE IF NOT EXISTS Users (
                                        id INTEGER PRIMARY KEY,
                                        name TEXT NOT NULL,
                                        email TEXT NOT NULL
                                    );"""
        c = conn.cursor()
        c.execute(sql_create_users_table)
    except Error as e:
        print(e)


def insert_message(conn, user_id, role, message):
    try:
        sql_insert_message = """INSERT INTO Conversations (user_id, role, message)
                                VALUES (?, ?, ?)"""
        cur = conn.cursor()
        cur.execute(sql_insert_message, (user_id, role, message))
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(e)


def insert_user(conn, user_id):
    try:
        sql_insert_user = """INSERT INTO Users (id) VALUES (?)"""
        cur = conn.cursor()
        cur.execute(sql_insert_user, (user_id,))
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(e)

def get_conversation_history(conn, user_id):
    try:
        cur = conn.cursor()
        cur.execute("SELECT role, message FROM Conversations WHERE user_id = ?", (user_id,))
        rows = cur.fetchall()
        chat_history = [{"role": row[0], "content": row[1]} for row in rows]
        return chat_history
    except Error as e:
        print(e)
