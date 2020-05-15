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


@app.route("/main", methods=["POST"])
def main():
    name = request.form.get("name")
    pwd = request.form.get("password")
    sqlString = f"SELECT * FROM users WHERE username= '{name}';"
    userrecord = db.execute(sqlString).fetchone()
    if userrecord is not None:
        if name == userrecord.username and pwd == userrecord.password:
            session['user'] = name
            return render_template("main.html",error=0)
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

@app.route("/results",methods=["POST"])
def results():
    author = request.form.get("author")
    isbn = request.form.get("isbn")
    title = request.form.get("title")

    if title != "":
        sqlString = f"SELECT * FROM books WHERE title LIKE  '%{title}%';"
    elif isbn != "":
        sqlString = f"SELECT * FROM books WHERE isbn LIKE '{isbn}%';"
    elif author != "":
        sqlString = f"SELECT * FROM books WHERE author LIKE '%{author}%';"
    else:
        #No values entered
        return render_template("main.html",error=1)
    
    books = db.execute(sqlString).fetchall()
    
    datalist = []
    return render_template("search_results.html",books=books,data=datalist)
    
    for book in books:
        #print(f"{book.isbn:<15}{book.title:<30}{book.author:<30}")
        isbn = book.isbn
        if len(isbn)==9: isbn = '0'+isbn        
        #res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "HG8RtIxpIH6ZPZbdN45bfw", "isbns":{isbn} })
        
        if res.status_code != 200:
            datalist.append(['-','-','-'])
        else:
            data=res.json()
            bookdata=data["books"]

            average      = bookdata[0]["average_rating"]
            rate_count   = bookdata[0]['ratings_count']
            review_count = bookdata[0]['reviews_count']
            datalist.append([average,rate_count,review_count])
        return render_template("search_results.html",books=books,data=datalist)
     


        
    

    
