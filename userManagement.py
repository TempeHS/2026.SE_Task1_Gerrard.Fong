import sqlite3 as sql
import bcrypt


### example
def getUsers():
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT email, password FROM users")
    users = cur.fetchall()
    con.close()
    return cur


def insertUser(email, password):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT email FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    if user:
        con.close()
        return False, "Email already registered"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    cur.execute(
        "INSERT INTO users (email, password) VALUES (?,?)", (email, hashed_password)
    )
    con.commit()
    con.close()


def loginUser(email, password):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT id, password FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    con.close()
    if user:
        user_id, stored_password = user
        if password == stored_password:
            return user_id
        else:
            return None
    else:
        return None
