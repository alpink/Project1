import csv
import os
import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    sqlString = "CREATE TABLE reviews(id INT PRIMARY KEY, username VARCHAR NOT NULL, date DATE, rating INT NOT NULL, review VARCHAR);"
    db.execute(sqlString)
    db.commit()
    


if __name__ == "__main__":
    main()

