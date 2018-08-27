from flask import Flask, flash, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import requests
import datetime
import os


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(os.path.join(os.path.dirname(os.path.abspath(__file__)), "message.db"))
db = SQLAlchemy(app)
Session(app)

class UserMessage(db.Model):
	id 		= db.Column(db.Integer	  ,	primary_key=True	,autoincrement=True)
	name 	= db.Column(db.String(128), nullable=True)
	email 	= db.Column(db.String(128), nullable = False)
	message = db.Column(db.String(512), nullable = False)
	msg_date= db.Column(db.DateTime   , nullable=False		,default=datetime.datetime.now)

	def __init__(self, name, email, message):
	   self.name = name
	   self.email = email
	   self.message = message
		
submit = ""
res = requests.get("http://data.fixer.io/api/latest", params={"access_key":"83bfbfdd2206026ccd7612f300662814"})

if res.status_code != 200:
    raise Exception("Error: Something went wrong!")

data = res.json()
unixdt = data["timestamp"]
tstamp = datetime.datetime.fromtimestamp(int(unixdt)).strftime('%Y-%m-%d %H:%M:%S')

@app.route("/")
def index():
    return render_template("index.html")
	
@app.route("/", methods=["POST"])
def message():
	if request.form:
		message = UserMessage(name=request.form.get("name"),email=request.form.get("email"),message=request.form.get("message"))
		db.session.add(message)
		db.session.commit()
		flash("Thank you! I'll reach you soon!")
		return render_template("message.html")	

   
@app.route("/crc")
def crc():
    headline = "Live foreign exchange rates and currency conversion apps | CRC"
    return render_template("crc.html", headlines = headline, data = data, submit=submit)

@app.route("/crc", methods = ["POST"])
def convert_currency():
    headline = "Live foreign exchange rates and currency conversion apps | CRC"
    userdbase   = request.form.get("defaultbase")
    userabase   = request.form.get("askingbase")
    quantity    = float(request.form.get("qty"))

    if not quantity:
        quantity = 1.00

    userdbaser  = float(data["rates"][userdbase])
    userabaser  = float(data["rates"][userabase])
    session["baserate"]     = userdbaser
    session["basecurrency"] = userdbase
    rate = round(round(userabaser/userdbaser,9) * quantity, 6)
    conversion = f"{ quantity } {userdbase} = {rate} {userabase}"
    return render_template("crc.html", headlines=headline, conversion = conversion, data = data)

@app.route("/all_currency")
def all_currency():
    headline = "Foreign exchange rates and currency conversion apps | CRC"
    return render_template("allcurrency.html", data = data, basecurrency = session["basecurrency"], baserate = session["baserate"],tstamp=tstamp,headlines=headline)
	
if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)	