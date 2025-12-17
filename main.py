from flask import Flask
from flask import redirect
from flask import render_template
from flask import request, session, url_for
from flask import jsonify
import requests
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
import pyotp
import pyqrcode
import base64
import os
import logging
import bcrypt
import userManagement as dbHandler

# Code snippet for logging a message
# app.logger.critical("message")

app_log = logging.getLogger(__name__)
logging.basicConfig(
    filename="security_log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)

# Generate a unique basic 16 key: https://acte.ltd/utils/randomkeygen
app = Flask(__name__)
app.secret_key = b"_53oi3uriq9pifpff;apl"
csrf = CSRFProtect(app)


@app.route("/enable_2fa", methods=["GET", "POST"])
def enable_2fa():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/index.html")

    if request.method == "POST":
        otp_input = request.form.get("otp", "").strip()
        user_secret = session.get("user_secret")

        if not user_secret:
            return render_template("/enable_2fa.html", error="Session expired")

        totp = pyotp.TOTP(user_secret)
        if totp.verify(otp_input):
            # Save secret to database
            dbHandler.save_2fa_secret(user_id, user_secret)
            session.pop("user_secret", None)
            return render_template(
                "/enable_2fa.html", success="2FA enabled successfully"
            )
        else:
            return render_template("/enable_2fa.html", error="Invalid OTP code")

    # Generate QR code for first time
    user_secret = pyotp.random_base32()
    session["user_secret"] = user_secret

    email = session.get("email", "user@example.com")
    totp = pyotp.TOTP(user_secret)
    otp_uri = totp.provisioning_uri(name=email, issuer_name="DevLogs")

    qr_code = pyqrcode.create(otp_uri)
    stream = BytesIO()
    qr_code.png(stream, scale=5)
    qr_code_b64 = base64.b64encode(stream.getvalue()).decode("utf-8")

    return render_template("/enable_2fa.html", qr_code=qr_code_b64, secret=user_secret)


@app.route("/verify_2fa", methods=["GET", "POST"])
def verify_2fa():
    email = session.get("temp_email")
    if not email:
        return redirect("/index.html")

    if request.method == "POST":
        otp_input = request.form.get("otp", "").strip()
        user_secret = dbHandler.get_2fa_secret(email)

        if not user_secret:
            return render_template("/verify_2fa.html", error="2FA not enabled")

        totp = pyotp.TOTP(user_secret)
        if totp.verify(otp_input):
            user_id = dbHandler.getUserIdByEmail(email)
            session["user_id"] = user_id
            session.pop("temp_email", None)
            return redirect("/form.html")
        else:
            return render_template("/verify_2fa.html", error="Invalid OTP code")

    return render_template("/verify_2fa.html")


# Redirect index.html to domain root for consistent UX
@app.route("/index", methods=["GET"])
@app.route("/index.htm", methods=["GET"])
@app.route("/index.asp", methods=["GET"])
@app.route("/index.php", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def root():
    return redirect("/", 302)


@app.route("/", methods=["POST", "GET"])
@csp_header(
    {
        # Server Side CSP is consistent with meta CSP in layout.html
        "base-uri": "'self'",
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": "'self' data:",
        "media-src": "'self'",
        "font-src": "'self'",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    }
)
def index():
    return render_template("/index.html")


@app.route("/signup.html", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("/signup.html")
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "").strip()
        if confirm_password == password:
            try:
                success = dbHandler.insertUser(email, password)
                if success:
                    user_id = dbHandler.loginUser(email, password)
                    session["user_id"] = user_id
                    return redirect("/form.html")
                else:
                    return render_template("/signup.html", error="Email already exists")
            except Exception as e:
                return render_template("/signup.html", error="Fail")
        else:
            return render_template("/signup.html", error="Passwords do not match")
    else:
        return render_template("/signup.html")


@app.route("/index.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user_id = dbHandler.loginUser(email, password)
        if user_id:
            if dbHandler.has_2fa_enabled(user_id):
                session["temp_email"] = email
                return redirect("/verify_2fa")

            session["user_id"] = user_id
            return redirect("/form.html")
        else:
            return render_template("/index.html", error="Invalid Credentials")


# example CSRF protected form
@app.route("/form.html", methods=["POST", "GET"])
def addLog():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=200)
    if request.method == "POST":

        user_id = session.get("user_id")
        if not user_id:
            return render_template("/index.html", error="Invalid Session")

        developer = request.form.get("developer", "").strip()
        start_time = request.form.get("start_time", "").strip()
        end_time = request.form.get("end_time", "").strip()
        time_worked = request.form.get("time_worked", "").strip()
        descriptions = request.form.get("descriptions", "").strip()
        status = request.form.get("status", "").strip()

        if not all([developer, start_time, end_time, time_worked, descriptions]):
            return render_template(
                "/form.html", error="Some fields are missing", login=True
            )

        dbHandler.insertLog(
            user_id,
            developer,
            start_time,
            end_time,
            time_worked,
            descriptions,
            status,
        )

        return redirect("/viewlogs.html")

    else:
        return render_template("/form.html", login=True)


@app.route("/viewlogs.html", methods=["GET", "POST"])
def viewLogs():
    logs = dbHandler.viewLogs(None)
    user_id = session.get("user_id")
    if not user_id:
        return render_template("/index.html", error="Invalid Session")
    personal_logs = dbHandler.viewLogs(user_id)
    if request.method == "POST":

        if "sort_start_time" in request.form:
            logs = dbHandler.sortTime("start_time", "DESC")
            personal_logs = dbHandler.sortTime("start_time", "DESC")

        elif "sort_end_time" in request.form:
            logs = dbHandler.sortTime("end_time", "DESC")
            personal_logs = dbHandler.sortTime("end_time", "DESC")

        elif "sort_time_worked" in request.form:
            logs = dbHandler.sortTime("time_worked", "DESC")
            personal_logs = dbHandler.sortTime("time_worked", "DESC")

        elif "sort_developer" in request.form:
            logs = dbHandler.sortDeveloper("DESC")
            personal_logs = dbHandler.sortDeveloper("DESC")

    else:
        logs = dbHandler.viewLogs(None)
        personal_logs = dbHandler.viewLogs(user_id)

    return render_template(
        "/viewlogs.html", logs=logs, personal_logs=personal_logs, login=True
    )


@app.route("/changelogs.html", methods=["POST", "GET"])
def changeLogs():
    user_id = session.get("user_id")
    if not user_id:
        return render_template("/index.html", error="Invalid Session")

    personal_logs = dbHandler.viewLogs(user_id)

    if request.method == "POST":

        developer = request.form.get("developer", "").strip()
        start_time = request.form.get("start_time", "").strip()
        end_time = request.form.get("end_time", "").strip()
        time_worked = request.form.get("time_worked", "").strip()
        descriptions = request.form.get("descriptions", "").strip()
        status = request.form.get("status", "").strip()
        log_id = request.form.get("log_id", "").strip()

        if "delete_log" in request.form:
            if not log_id:
                return render_template(
                    "/changelogs.html",
                    personal_logs=personal_logs,
                    error="Log ID is required",
                    login=True,
                )

            dbHandler.removeLog(log_id, user_id)
            return redirect("/changelogs.html")

        if "update_log" in request.form:
            if not all(
                [developer, start_time, end_time, time_worked, descriptions, log_id]
            ):
                return render_template(
                    "/changelogs.html",
                    personal_logs=personal_logs,
                    error="Some fields are missing",
                    login=True,
                )

            dbHandler.changeLog(
                developer,
                start_time,
                end_time,
                time_worked,
                descriptions,
                status,
                log_id,
                user_id,
            )
        return redirect("/viewlogs.html")

    return render_template("/changelogs.html", personal_logs=personal_logs, login=True)


# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data.decode())
    return "done"


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
