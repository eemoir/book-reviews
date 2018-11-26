import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
	db.execute("CREATE TABLE reviews(user_id INT references users(id), user_name VARCHAR, ISBN VARCHAR, text VARCHAR(1000), rating NUMERIC)")
	db.commit()

if __name__ == "__main__":
	main()