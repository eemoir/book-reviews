import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
	db.execute("CREATE TABLE books(id SERIAL PRIMARY KEY, ISBN VARCHAR(30), title VARCHAR(256), author VARCHAR(256), year VARCHAR(10))")
	f = open("books.csv")
	reader = csv.reader(f)
	for isbn, title, author, year in reader:
		db.execute("INSERT INTO books (ISBN, title, author, year) VALUES (:ISBN, :title, :author, :year)", 
			{"ISBN": isbn, "title": title, "author": author, "year": year})
	db.commit()


if __name__ == "__main__":
	main()