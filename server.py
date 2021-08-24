from flask import Flask,request,jsonify
import json
import sqlite3

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "maxmaxmaxsupermaxmaxmaxsupermaxmaxmaxsuperupermaxmaxmaxmax"
jwt = JWTManager(app)


def db_connection():
	try:
		conn = sqlite3.connect('books.sqlite')
		print("Connected")
	except:
		print("Failed")
	return conn

@app.route("/login", methods=["POST"])
def login():
    conn  = db_connection()
    cursor = conn.cursor()
    request_username = request.json.get("username", None)
    request_password = request.json.get("password", None)
    cursor.execute("SELECT * FROM user WHERE username=?", (request_username,))
    user = list(cursor.fetchone())
    if user != [] and (user[1] != request_username or user[2] != request_password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=request_username)
    return jsonify(access_token=access_token)
    
@app.route("/signup",methods=["POST"])
def signup():
    conn  = db_connection()
    cursor = conn.cursor()
    new_username = request.json.get("username", None)
    new_password = request.json.get("password", None)
    if new_username is not None and new_password is not None:
        sql = """INSERT INTO user (username,password) VALUES (?,?)"""
        cursor = cursor.execute(sql,(new_username,new_password))
        conn.commit()
        conn.close()
        return "Sucess",201
    return "Failed",401
    

@app.route("/books",methods=["GET","POST"])
@jwt_required()
def books():
	conn  = db_connection()
	cursor = conn.cursor()
	if request.method == "GET":
		cursor = conn.execute("SELECT * FROM book")
		books = [dict(id=row[0],author=row[1],title=row[2]) for row in cursor.fetchall()]
		if books is not None:
			return jsonify(books)
	if request.method == "POST":
		new_author = request.json.get("author", None)
		new_title = request.json.get("title", None)
		sql = """INSERT INTO book (author,title) VALUES (?,?)"""
		cursor = cursor.execute(sql,(new_author,new_title))
		conn.commit()
	conn.close()
	return "Sucess",201
		
@app.route("/book/<int:id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def single_book(id):
    conn = db_connection()
    cursor = conn.cursor()
    book = None
    if request.method == "GET":
        cursor.execute("SELECT id,author,title FROM book WHERE id=?", (id,))
        row = cursor.fetchone()
        dict  = {"id":row[0],"author":row[1],"title":row[2]}
        print(dict)
        book = jsonify(dict)
        if book is not None:
            return book, 200
        else:
            return "Something wrong", 404

    if request.method == "PUT":
        sql = """UPDATE book
                SET title=?,
                    author=?
                WHERE id=? """

        author = request.json.get("author", None)
        title = request.json.get("title", None)
        updated_book = {
            "id": id,
            "author": author,
            "title": title
        }
        print(id)
        conn.execute(sql, (title, author, id))
        conn.commit()
        return jsonify(updated_book)

    if request.method == "DELETE":
        sql = """ DELETE FROM book WHERE id=? """
        conn.execute(sql, (id,))
        conn.commit()
        return "The book with id: {} has been deleted.".format(id), 200
        
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


if __name__ == "__main__":
	app.run(debug=True)
