import os
import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    booklist = db.execute("SELECT * FROM books;").fetchall()
    for book in booklist:
        print(book)


if __name__ == "__main__":
    main()

