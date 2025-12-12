import sqlite3 as sql
import bcrypt


### example
def getUsers():
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT password FROM users")
    passwords = cur.fetchall()
    con.close()
    list_passwords = []
    for password in passwords:
        password = password.decode("utf-8")
        list_passwords.append(password)
    return list_passwords


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
    cur.execute("SELECT password FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    con.close()

    hashed_password = user[0]
    if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
        con = sql.connect("databaseFiles/database.db")
        cur = con.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_result = cur.fetchone()
        con.close()
        return user_result[0]
