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
    return True


def loginUser(email, password):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT password FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    con.close()

    if user is None:
        return None

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


def removeLog(log_id, user_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute(
        "DELETE FROM logs WHERE id=? AND user_id=?",
        (
            log_id,
            user_id,
        ),
    )
    con.commit()
    con.close()


def changeLog(
    developer, start_time, end_time, time_worked, descriptions, status, log_id, user_id
):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute(
        "UPDATE logs SET developer=?, start_time=?, end_time=?, time_worked=?, descriptions=?, status=? WHERE id=? AND user_id=?",
        (
            developer,
            start_time,
            end_time,
            time_worked,
            descriptions,
            status,
            log_id,
            user_id,
        ),
    )
    con.commit()
    con.close()


def viewLogs(user_id=None):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    if user_id:
        log = cur.execute(
            "SELECT * FROM logs WHERE user_id=? ORDER BY id DESC", (user_id,)
        )
    else:
        log = cur.execute("SELECT * FROM logs WHERE status!='Hidden' ORDER BY id DESC")

    results = log.fetchall()
    con.close()
    return results


def sortTime(time, sort):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    query = f"SELECT * FROM logs WHERE status!='Hidden' ORDER BY {time} {sort}"
    logs = cur.execute(query)
    results = logs.fetchall()
    con.close()
    return results


def sortDeveloper(sort):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    query = f"SELECT * FROM logs WHERE status!='Hidden' ORDER BY developer {sort}"
    logs = cur.execute(query)
    results = logs.fetchall()
    con.close()
    return results


def save_2fa_secret(user_id, secret):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET two_fa_secret = ? WHERE id = ?", (secret, user_id))
    con.commit()
    con.close()


def get_2fa_secret(email):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT two_fa_secret FROM users WHERE email = ?", (email,))
    result = cur.fetchone()
    con.close()
    return result[0] if result else None


def has_2fa_enabled(user_id):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT two_fa_secret FROM users WHERE id = ?", (user_id,))
    result = cur.fetchone()
    con.close()
    return result[0] is not None if result else False


def getUserIdByEmail(email):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    result = cur.fetchone()
    con.close()
    return result[0] if result else None
