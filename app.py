from datetime import datetime
import requests
import email
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request

app = Flask(__name__)
OUTPUTS = {}



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route("/about.html")
def about():
    return render_template("about.html")
@app.route("/products.html")
def products():
    return render_template("products.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    username = request.form.get("mail")
    
    if not name:
        return render_template("error.html", message="Please Enter District ID")
    if not username:
        return render_template("error.html", message="Please Enter Mail ID")

    else:
        def get_sessions(data):
            for center in data["centers"]:
                for session in center["sessions"]:
                    yield {"name": center["name"],
                           "type": center["fee_type"],
                           "date": session["date"],
                           "capacity": session["available_capacity"],
                           "age_limit": session["min_age_limit"],
                           "vaccine": session["vaccine"],
                           "pincode":center["pincode"]
                           }

        def get_for_seven_days(start_date):
            resp = requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict",
                                params={"district_id": name, "date": start_date.strftime("%d-%m-%Y")}, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"})
            data = resp.json()
            return [session for session in get_sessions(data) if session["capacity"] > 0 and session["age_limit"] == 18]

        def create_output(session_info):
            return f"{session_info['date']} , {session_info['name']},(pincode: {session_info['pincode']}), (Capacity: {session_info['capacity']}) ,{session_info['vaccine']}, {session_info['type']}"

        content = "\n".join([create_output(session_info) for session_info in get_for_seven_days(datetime.now())])
        
        sender = "slotavailibility12345@gmail.com"
        sender_password = "pblMHTBC@12345"

        if not content:
            return render_template("noavailable.html",message="No slots available for your region")
        else:
            username = request.form.get("mail")
            email_msg = email.message.EmailMessage()
            email_msg["Subject"] = "Vaccination Slot Open"
            email_msg["From"] = username
            email_msg["To"] = username
            email_msg.set_content(content)

            with smtplib.SMTP(host='smtp.gmail.com', port='587') as server:
                smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
                smtpserver.starttls()
                smtpserver.ehlo()
                smtpserver.login(sender, sender_password)
                smtpserver.send_message(email_msg)
            return render_template("output.html",message="Check Your Mail For Report" )
        


if __name__ == '__main__':
    app.debug = True
    app.run()
