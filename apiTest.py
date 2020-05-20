#testing the API calls
import re
import os

from datetime import date
from flask import Flask, session, render_template, request 
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy import cast,Date
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

def extract(widget):
    pattern = "<iframe(.*?)</iframe>"
    substring = re.search(pattern, widget).group(1)
    substring='<iframe '+substring+'</iframe>'
    return substring

    

def test():
    author = "cat"
    isbn   = ""
    title  = ""
    #author = request.form.get("author")
    #isbn = request.form.get("isbn"):
    #title = request.form.get("title")
    sqlString = f"SELECT * FROM books WHERE author like '%{author}%'"
    books = db.execute(sqlString).fetchall()
    for book in books:
        print(book)
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "HG8RtIxpIH6ZPZbdN45bfw", "isbns": book.isbn})
        data = res.json()
        details = data["books"][0]
        ratings_count = details["ratings_count"]
        review_count  = details["reviews_count"]
        average_rating = details["average_rating"]
        print(ratings_count,review_count,average_rating )
    print()

def test2():
    #db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year);",{"isbn": isbn, "title": title, "author": author, "year": year})        
    rating=4
    review="Good"
    isbn="0265748999"
    username = "Bob"
    sqlstring = f"INSERT INTO reviews (username, rating, review, isbn) VALUES ('{username}', {rating}, '{review}', '{isbn}');"
    print(sqlstring)
    #db.execute("INSERT INTO reviews (username, rating, review, isbn) VALUES (:username :rating :review :isbn);" ,{"username": username, "rating": rating, "review": review, "isbn": isbn})
    #db.execute("INSERT INTO reviews (username, rating, review, isbn) VALUES ('Bob', 4, 'Good', '0265748999');)
    db.commit()

username='Anne'
isbn='1400033411'
sqlstring = f"SELECT * FROM reviews WHERE username='{username}' AND isbn='{isbn}';"
print(sqlstring)
results = db.execute(sqlstring).first()
if results==None:
    print('already exists')
else:
    print('new')




