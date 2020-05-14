import os

from flask import Flask, session, render_template, request 
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = b'12345678'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    session['user']=""
    return render_template("index.html", code="")

@app.route("/register")
def register():
    #userlist = db.execute("SELECT * FROM users;").fetchall()
    return render_template("register.html")

@app.route("/logoff")
def logoff():
    session['user']=""
    return render_template("index.html", code="")


@app.route("/logon", methods=["POST"])
def logon():
    name = request.form.get("name")
    pwd = request.form.get("password")
    sqlString = f"SELECT * FROM users WHERE username= '{name}';"
    userrecord = db.execute(sqlString).fetchone()
    if userrecord is not None:
        if name == userrecord.username and pwd == userrecord.password:
            session['user'] = name
            return render_template("main.html")
        else:
            return render_template("index.html", code=404)
    else:
        return render_template("index.html", code=404)

@app.route("/adduser", methods=["POST"])
def adduser():
    name = request.form.get("name")
    pwd = request.form.get("password")
    sqlString = f"INSERT INTO users (username, password) VALUES ('{name}','{pwd}');"
    db.execute(sqlString)
    db.commit()
    return render_template("index.html", code="new")

