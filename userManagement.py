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


def insertLog(
    user_id, developer, start_time, end_time, time_worked, descriptions, status
):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO logs (user_id, developer, start_time, end_time, time_worked, descriptions, status) VALUES (?,?,?,?,?,?,?)",
        (user_id, developer, start_time, end_time, time_worked, descriptions, status),
    )
    con.commit()
    con.close()


def editLog(log_id, developer, start_time, end_time, time_worked, descriptions, status):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute(
        "UPDATE logs SET developer=?, start_time=?, end_time=?,time_worked=?, descriptions=?, status=? WHERE id=?",
        (developer, start_time, end_time, time_worked, descriptions, status, log_id),
    )
    con.commit()
    con.close()


def removeLog(log_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("DELETE FROM logs WHERE id=?", (log_id,))
    con.commit()
    con.close()


def viewLogs():
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    logs = cur.execute("SELECT * FROM logs")
    results = logs.fetchall()
    con.close()
    return results


def sortTime():
    pass


def sortDeveloper():
    pass
