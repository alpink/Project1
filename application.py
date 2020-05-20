import os
import re
from datetime import date

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy import cast, Date
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

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
    session['user']=None
    return render_template("index.html", code="")

@app.route("/register")
def register():
    #userlist = db.execute("SELECT * FROM users;").fetchall()
    return render_template("register.html")

@app.route("/logoff")
def logoff():
    session["user"]=None
    return render_template("index.html", code="")

@app.route("/main", methods=["POST","GET"])
def main():
    if session.get("user") is None:
        name = request.form.get("name")
        pwd = request.form.get("password")
        sqlString = f"SELECT * FROM users WHERE username= '{name}';"
        userrecord = db.execute(sqlString).fetchone()
        if userrecord is not None:
            if name == userrecord.username and pwd == userrecord.password:
                session['user'] = name
                print(name)
                return render_template("main.html",user=name,error=0)
            else:
                return render_template("index.html", error=1)
        else:
            return render_template("index.html", error=404)
    else:
        print("Existing")
        user = session.get("user")
        print(user)
        return render_template("main.html",user=user,error=0)

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
    return render_template("searchresults.html",books=books)

@app.route("/bookdetails", methods=["POST"])
def bookdetails():
    author = request.form.get("author")
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "HG8RtIxpIH6ZPZbdN45bfw", "isbns": {isbn}})
    data = res.json()
    details = data["books"][0]
    ratings_count = details["ratings_count"]
    review_count  = details["reviews_count"]
    average_rating = details["average_rating"]
    bookID = details["id"]

    res = requests.get(f"https://www.goodreads.com/book/isbn/{isbn}",params={"format": "json", "key": "HG8RtIxpIH6ZPZbdN45bfw"})
    data=res.json()
    if res.status_code == 200:
        pattern = "<iframe(.*?)</iframe>"
        substring = re.search(pattern, data["reviews_widget"]).group(1)
        substring='<iframe '+substring+'</iframe>'
        f = open("templates\widget.html","w")
        f.write(substring)
        f.close()
    
    return render_template("search_results2.html",title=title,author=author,ratings=ratings_count,reviews=review_count,average=average_rating,bookID=bookID,isbn=isbn)

@app.route("/addreview", methods=["POST"])
def addreview():
    isbn=request.form.get("isbn")
    title=request.form.get("title")
    author=request.form.get("author")
    print(author,title,isbn)
    return render_template("reviewform.html",title=title,author=author,isbn=isbn)


@app.route("/addnewreview", methods=["POST"])
def addnewreview():
    username = session.get("user")
    isbn= request.form.get("isbn")
    sqlstring = f"SELECT * FROM reviews WHERE username='{username}' AND isbn={isbn};"
    results = db.execute(sqlstring).first()
    if results==None:
        rating=request.form.get("rate")
        review=request.form.get("review")
        title=request.form.get("title")
        author=request.form.get("author")
        print(isbn)
        sqlstring = f"INSERT INTO reviews (username, title, author, rating, review, isbn) VALUES ('{username}', {title},{author},{rating}, '{review}', {isbn});"
        db.execute(sqlstring)
        db.commit()
    reviews = db.execute(f"SELECT * FROM reviews WHERE username='{username}';").fetchall()
    return render_template("myreviews.html",reviews=reviews)

@app.route("/myreviews")
def myreviews():
    username = session.get("user")
    print("username:",username)
    sql = f"SELECT * FROM reviews WHERE username='{{username}}';"
    print("sql: ",sql)
    reviews = db.execute(f"SELECT * FROM reviews WHERE username='{username}';").fetchall()
    return render_template("myreviews.html",reviews=reviews)

@app.route("/api/<string:isbn>")
def api_isbn(isbn):
    print(isbn)
    book = db.execute(f"SELECT * FROM books WHERE isbn='{isbn}';").fetchone()
    if book != None:
        title=book.title
        author=book.author
        year=book.year
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "HG8RtIxpIH6ZPZbdN45bfw", "isbns": {isbn}})
        data = res.json()
        details = data["books"][0]
        review_count  = details["reviews_count"]
        average_rating = details["average_rating"]
        jsonString = jsonify({
            "title": title,
            "author": author,
            "year": year,
            "isbn": isbn,
            "review_count": review_count ,
            "average_score": average_rating
        })
    else:
        jsonString ="ISBN not found"
        
    return jsonString
        

    
    
    
