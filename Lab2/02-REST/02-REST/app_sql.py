from flask import Flask, request, jsonify, g
import sqlite3

app = Flask(__name__)
DATABASE = 'library.db'

# Function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # To access columns by name
    return db

# Function to execute a query
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# Function to modify the database
def modify_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    cur.close()

# Create books table if it doesn't exist
with app.app_context():
    query_db('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL
        )
    ''')
##################################################### added code #####################################################
# Create members table if it doesn't exist
with app.app_context():
    query_db('''
        CREATE TABLE IF NOT EXISTS members (   
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL 
        )   
    ''')   
#####################################################           #####################################################

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/books', methods=['GET'])
def get_books():
    books = query_db('SELECT * FROM books')
    book_list = [{"id": book[0], "title": book[1], "author": book[2]} for book in books]
    return jsonify(book_list)

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = query_db('SELECT * FROM books WHERE id = ?', (book_id,), one=True)
    if book is None:
        return "Book not found", 404
    return jsonify({"id": book[0], "title": book[1], "author": book[2]})

@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    modify_db('INSERT INTO books (title, author) VALUES (?, ?)', (data["title"], data["author"]))
    new_book_id = query_db('SELECT last_insert_rowid()')[0][0]
    return jsonify({"id": new_book_id, "title": data["title"], "author": data["author"]}), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    book = query_db('SELECT * FROM books WHERE id = ?', (book_id,), one=True)
    if book is None:
        return "Book not found", 404
    modify_db('UPDATE books SET title = ?, author = ? WHERE id = ?', (data["title"], data["author"], book_id))
    return jsonify({"id": book_id, "title": data["title"], "author": data["author"]})

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = query_db('SELECT * FROM books WHERE id = ?', (book_id,), one=True)
    if book is None:
        return "Book not found", 404
    modify_db('DELETE FROM books WHERE id = ?', (book_id,))
    return "Book deleted", 204

##################################################### added code #####################################################

@app.route('/members',  methods=['GET'])
def get_members():   
    members = query_db('SELECT * FROM members')   
    member_list = [{"id": member[0], "name": member[1], "email": member[2]} for member in members]
    return jsonify(member_list)   
   
@app.route('/members/<int:member_id>', methods=['GET'])   
def get_member(member_id):   
    member = query_db('SELECT * FROM members WHERE id = ?', (member_id,), one=True)
    if member is None:   
        return "Member not found", 404   
    return jsonify({"id": member[0], "name": member[1], "email": member[2]})   
   
@app.route('/members', methods=['POST'])   
def create_member():   
    data = request.get_json()   
    modify_db('INSERT INTO members (name, email) VALUES (?, ?)', (data["name"], data["email"]))   
    new_member_id = query_db('SELECT last_insert_rowid()')[0][0]   
    return jsonify({"id": new_member_id, "name": data["name"], "email": data["email"]}), 201   
   
@app.route('/members/<int:member_id>', methods=['PUT'])   
def update_member(member_id):   
    data = request.get_json()   
    member = query_db('SELECT * FROM members WHERE id = ?', (member_id,), one=True)   
    if member is None:   
        return "Member not found", 404   
    modify_db('UPDATE members SET name = ?, email = ? WHERE id = ?', (data["name"], data["email"], member_id))   
    return jsonify({"id": member_id, "name": data["name"], "email": data["email"]})   
            
@app.route('/members/<int:member_id>', methods=['DELETE'])                          
def delete_member(member_id):
    member = query_db('SELECT * FROM members WHERE id = ?', (member_id,), one=True)
    if member is None:
        return "Member not found", 404              
    modify_db('DELETE FROM members WHERE id = ?', (member_id,))        
    return "Member deleted", 204        
#####################################################            #####################################################

if __name__ == '__main__':
    app.run(debug=True)
