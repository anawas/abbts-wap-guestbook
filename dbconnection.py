# Wir nutzen zu Demozwecken die SQLite-DB
import sqlite3
from dataclasses import dataclass

from werkzeug.security import check_password_hash, generate_password_hash

import config


@dataclass
class Entry:
    user: str
    message: str
    date: str


def init_data() -> None:
    # Wir müssen in jeder Funktion eine separate
    # Verbindung öffnen, da SQLite nicht mit verschiedenen
    # Threads funktioniert.
    con = sqlite3.connect("guestbook.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE entries(user, message, date)")
    cur.execute("CREATE TABLE users(user, password, role)")

    # Ein paar Einträge ins Buch eintragen
    cur.execute("""
        INSERT INTO entries VALUES
        ("andreas", "Toll!", "2023-06-12"),
        ("bart", "Wonderful!!!", "2023-10-13"),
        ("CLAUDIA++", "Ich verstehe die Aufregung nicht", "2024-12-21")
    """)

    # Das Login für den Admin setzen
    passwd_hash = generate_password_hash(config.ADMIN_PASSWORD)
    cur.execute(f"""
        INSERT INTO users VALUES
        ('admin', '{passwd_hash}', 'admin')
    """)
    con.commit()
    cur.close()
    con.close()


def get_entries() -> list[Entry]:
    con = sqlite3.connect("guestbook.db")

    entries = []
    cur = con.execute("""
        SELECT * from entries LIMIT 5
    """)
    resp = cur.fetchall()
    for entry in resp:
        entries.append(Entry(entry[0], entry[1], entry[2]))
    cur.close()
    con.close()
    return entries


def add_entry(user: str, msg: str, date: str) -> None:
    con = sqlite3.connect("guestbook.db")
    cur = con.cursor()
    cur.execute(f"""INSERT INTO entries VALUES
        ('{user}', '{msg}', '{date}')""")
    con.commit()
    cur.close()
    con.close()


def is_user_admin(user, password):
    con = sqlite3.connect("guestbook.db")
    cur = con.cursor()
    cur.execute(f"""SELECT * FROM users WHERE user = '{user}'""")

    resp = cur.fetchone()
    if resp is None:
        return None

    cur.close()
    con.close()

    if user == resp[0] and check_password_hash(resp[1], password):
        return resp[0]
    return None


def delete_user(user):
    con = sqlite3.connect("guestbook.db")
    cur = con.cursor()
    cur.execute(f"""DELETE FROM entries WHERE user = '{user}'""")
    con.commit()
    cur.close()
    con.close()


# Wir diese Datei direkt aufgerufen wird die DB initialisert
if __name__ == "__main__":
    init_data()
