#testing the API calls

import os

from flask import Flask, session, render_template, request 
from flask_session import Session
from sqlalchemy import create_engine
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


def test():
    author = "cat"
    isbn   = ""
    title  = ""
    #author = request.form.get("author")
    #isbn = request.form.get("isbn")
    #title = request.form.get("title")
    sqlString = f"SELECT * FROM books WHERE author like '%{author}%'"
    books = db.execute(sqlString).fetchall()
    

    for book in books:
        print(f"{book.isbn:<15}{book.title:<30}{book.author:<30}")
    
        #now get ratings
        isbn = book.isbn
        if len(isbn)==9: isbn = '0'+isbn
        #print(isbn)
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "HG8RtIxpIH6ZPZbdN45bfw", "isbns":{isbn} })
        #print(res)
        data=res.json()
        #print(data)
        bookdata=data["books"]

        average      = bookdata[0]["average_rating"]
        rate_count   = bookdata[0]['ratings_count']
        review_count = bookdata[0]['reviews_count']
        
        print(f"There are {rate_count} ratings and {review_count} reviews. The average rating is {average}.")
        print()

test()




