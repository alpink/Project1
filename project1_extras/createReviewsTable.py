import csv
import os
import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("users.csv")
    reader = csv.reader(f)
    for username,password in reader:
        db.execute("INSERT INTO users (username, password) VALUES (:username , :password)",
                    {"username": username, "password": password})
        print(f"Added {username} with password {password}.")
    db.commit()


if __name__ == "__main__":
    main()

