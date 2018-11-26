import os
import requests
import json

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt

app = Flask(__name__, static_folder='static')

api_key = 'IwMnmen4tRRfuHdZokOVhA'
DATABASE_URL = 'postgres://cghbqrfqowdymj:2dcc5fad292bb8adfd6eff9577b639deccda3ecd196d71db42ff97e9dcac853b@ec2-54-83-4-76.compute-1.amazonaws.com:5432/dbv1nb3dcq16er'

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
	if 'user_id' not in session:
		return render_template("index.html")
	else: 
		return redirect(url_for('search'))

@app.route("/register", methods=["POST", "GET"])
def register():
	if request.method == "GET":
		return render_template("registration.html")
	elif request.method == "POST": 
		username = request.form.get('username')
		password = request.form.get('password')
		if db.execute("SELECT FROM users WHERE username=:username", {"username": username}).rowcount > 0:
			return render_template("registration.html", username=username, error_message="This username is already taken.")
		else:
			if not (any(x.isupper() for x in password) and any(x.islower() for x in password) and any(x.isdigit() for x in password) and (len(password) >= 10)):
				return render_template("registration.html", username=username, error_message="Invalid password.")
			else: 	
				h = sha256_crypt.encrypt(password)
				db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", 
					{"username": username, "password": h})
				db.commit()
				user_id = db.execute("SELECT id FROM users WHERE username=:username", {"username": username}).fetchone()
				if user_id is None:
					return render_template("registration.html", error_message="There was an error registering. Please try again.")
				else:
					session['user_id'] = user_id[0]
					session['user_name'] = username
					return redirect(url_for('search'))

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		if 'user_id' in session: 
			return redirect(url_for('search'))
		else: 
			return render_template("login.html")
	else:
		username = request.form.get('username')
		password = request.form.get('password')
		if username == '' or password == '':
			return render_template("login.html", 
				error_message="Please enter username and password.")
		if not db.execute("SELECT FROM users WHERE username=:username", {"username": username}).rowcount == 1:
			return render_template("login.html", 
				error_message="Login error. Please try again.")
		h = db.execute("SELECT password FROM users WHERE username=:username", {"username": username}).fetchone()
		if not sha256_crypt.verify(password, h[0]):
			return render_template("login.html", 
				error_message="Login error. Please try again.")
		else:
			user_id = db.execute("SELECT id FROM users WHERE username=:username", {"username": username}).fetchone()
			session['user_id'] = user_id[0]
			session['user_name'] = username
			return redirect(url_for('search'))

@app.route("/logout")
def logout():
	if 'user_id' in session: 
		del session["user_id"]
		del session["user_name"]
		return redirect(url_for('index'))
	else: 
		return redirect(url_for('index'))

@app.route("/search", methods=["GET", "POST"])
def search():
	if 'results' in session:
		del session['results']
	if 'author_results' in session:
		del session['author_results']
	if 'user_id' not in session:
		return render_template("index.html")
	else: 
		if request.method == "GET":
			return render_template("search.html", 
				username=session['user_name'])
		else: 
			title = request.form.get('title')
			author = request.form.get('author')
			ISBN = request.form.get('ISBN')
			if not title == '':
				if not author == '':
					if not ISBN == '':
						search = db.execute("SELECT * FROM books WHERE UPPER(title) LIKE UPPER(:title) AND UPPER(author) LIKE UPPER(:author) AND UPPER(ISBN) LIKE UPPER(:ISBN)", {"title": "%" + title + "%", "author": "%" + author + "%", "ISBN": "%" + ISBN + "%"}).fetchall()
						if len(search) == 0:
							return render_template('search.html', 
								error_message="No results found",
								username=session['user_name'])
						else:
							session['results'] = search
							return redirect(url_for('results'))
					else:
						search = db.execute("SELECT * FROM books WHERE UPPER(title) LIKE UPPER(:title) AND UPPER(author) LIKE UPPER(:author)", {"title": "%" + title + "%", "author": "%" + author + "%"}).fetchall()
						if len(search) == 0:
							return render_template('search.html', 
								error_message="No results found",
								username=session['user_name'])
						else: 
							session['results'] = search
							return redirect(url_for('results'))
				else:
					search = db.execute("SELECT * FROM books WHERE UPPER(title) LIKE UPPER(:title)", {"title": "%" + title + "%"}).fetchall()
					if len(search) == 0:
						return render_template('search.html', 
							error_message="No results found",
							username=session['user_name'])
					else: 
						session['results'] = search
						return redirect(url_for('results'))
			else:
				if not author == '':
					if not ISBN == '':
						search = db.execute("SELECT * FROM books WHERE UPPER(author) LIKE UPPER(:author) AND UPPER(ISBN) LIKE UPPER(:ISBN)", {"author": "%" + author + "%", "ISBN": "%" + ISBN + "%"}).fetchall()
						if len(search) == 0:
							return render_template('search.html', 
								error_message="No results found",
								username=session['user_name'])
						else: 
							session['results'] = search
							return redirect(url_for('results'))
					else:
						search = db.execute("SELECT author FROM books WHERE UPPER(author) LIKE UPPER(:author)", {"author": "%" + author + "%"}).fetchall()
						if len(search) == 0:
							return render_template('search.html', 
								error_message="No results found",
								username=session['user_name'])
						else: 
							results = set()
							for item in search:
								results.add(item[0])
							session['author_results'] = results
							print(results)
							return redirect(url_for('author_search'))
				else: 
					if not ISBN == '':
						search = db.execute("SELECT * FROM books WHERE UPPER(ISBN) LIKE UPPER(:ISBN)", {"ISBN": "%" + ISBN + "%"}).fetchall()
						if len(search) == 0:
							return render_template('search.html', 
								error_message="No results found",
								username=session['user_name'])
						else: 
							session['results'] = search
							return redirect(url_for('results'))
					else:
						return render_template('search.html', 
							error_message="Please enter at least one search parameter",
							username=session['user_name'])	

@app.route("/results")
def results():
	if 'user_id' not in session:
		return render_template("index.html")
	else:
		if "results" in session:
			results = session['results']
			return render_template("results.html", 
				results=results, 
				username=session['user_name'])
		else:
			return redirect(url_for('search'))

@app.route("/author_search")
def author_search():
	if 'user_id' not in session:
		return render_template("index.html")
	else:
		if "author_results" in session: 
			author_results = session['author_results']
			return render_template("results.html", 
				author_results=author_results,
				username=session['user_name'])
		else:
			return redirect(url_for('search'))

@app.route("/author")
def author():
	if 'user_id' not in session:
		return render_template("index.html")
	author = request.args.get('author')
	if author:
		search = db.execute("SELECT * FROM books WHERE author=:author", {'author': author}).fetchall()
		session['results'] = search
		return redirect(url_for('results'))
	else:
		return redirect(url_for('search'))

@app.route("/book_details", methods=["GET", "POST"])
def details():
	if 'user_id' not in session:
		return render_template("index.html")
	if request.method == "GET":
		ISBN = request.args.get('ISBN')
		book = request.args.get('book')
		if ISBN:
			session['ISBN'] = ISBN
			session['book'] = book
			author = request.args.get('author')
			year = request.args.get('year')
			res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": ISBN})
			goodreads_rating = res.json()['books'][0]['average_rating']
			goodreads_number = res.json()['books'][0]['work_ratings_count']
			search = db.execute("SELECT * FROM reviews WHERE user_id=:id AND ISBN=:ISBN", {'id': session['user_id'], 'ISBN': ISBN}).fetchone()
			all_reviews = db.execute("SELECT * FROM reviews WHERE user_id!=:id and ISBN=:ISBN", {'id': session['user_id'], 'ISBN': ISBN}).fetchall()
			if search:
				if all_reviews:
					return render_template("details.html", 
						book=book, 
						author=author, 
						ISBN=ISBN, year=year, 
						goodreads=goodreads_rating, 
						number=goodreads_number, 
						my_review=search['text'], 
						my_rating=int(search['rating']), 
						all_reviews=(all_reviews),
						username=session['user_name'])
				else: 
					return render_template("details.html", 
						book=book, 
						author=author, 
						ISBN=ISBN, 
						year=year, 
						goodreads=goodreads_rating, 
						number=goodreads_number, 
						my_review=search['text'], 
						my_rating=int(search['rating']),
						username=session['user_name'])
			else:
				if all_reviews:
					return render_template("details.html", 
						book=book, 
						author=author, 
						ISBN=ISBN, 
						year=year, 
						goodreads=goodreads_rating, 
						number=goodreads_number, 
						all_reviews=(all_reviews),
						username=session['user_name'])
				else: 
					return render_template("details.html", 
						book=book, 
						author=author, 
						ISBN=ISBN, 
						year=year, 
						goodreads=goodreads_rating, 
						number=goodreads_number,
						username=session['user_name'])
		else:
			return render_template("search.html",
				username=session['user_name'])
	else:
		review = request.form.get('text')
		rating = int(request.form.get('rating'))
		db.execute("INSERT INTO reviews (user_id, user_name, ISBN, text, rating) VALUES (:user_id, :user_name, :ISBN, :text, :rating)", {"user_id": session['user_id'], "user_name": session['user_name'], "ISBN": session['ISBN'], "text": review, "rating": rating})
		db.commit()
		return render_template("submission.html", 
			book=session['book'],
			username=session['user_name']) 

@app.route("/api/<isbn>")
def api(isbn):
	entry = db.execute("SELECT * FROM books WHERE UPPER(ISBN)=UPPER(:ISBN)", {'ISBN': isbn}).fetchone()
	data = {}
	if entry:
		data['title']=entry['title']
		data['author']=entry['author']
		data['year']=entry['year']
		data['ISBN']=entry["isbn"]
		data['number_of_ratings'] = db.execute("SELECT COUNT(rating) FROM reviews WHERE ISBN=:ISBN", {'ISBN': data["ISBN"]}).fetchone()[0]
		if data['number_of_ratings'] == 0:
			data['rating'] = 'N/A'
		else:
			data['rating'] = float(db.execute("SELECT AVG(rating) from reviews WHERE ISBN=:ISBN", {'ISBN': data['ISBN']}).fetchone()[0])
			print(data['rating'])
		return json.dumps(data)
	else:
		data['Error']="No book with that ISBN found in database."
		return json.dumps(data)