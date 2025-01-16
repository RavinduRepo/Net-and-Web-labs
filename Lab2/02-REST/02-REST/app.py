from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample data as a dictionary keyed by book ID
books = {
    1: {"id": 1, "title": "Book 1", "author": "Author 1"},
    2: {"id": 2, "title": "Book 2", "author": "Author 2"},
    3: {"id": 3, "title": "Book 3", "author": "Author 3"},
}

# Sample data as a dictionary keyed by user ID
members = {
    123: {"id": 123, "name": "User 1", "email": "user1@example.com"},
    456: {"id": 456, "name": "User 2", "email": "user2@example.com"},
}

# Sample data as a dictionary keyed by loan ID
loans = {}

# Generate unique IDs for new items
def generate_id(dictionary):
    return max(dictionary.keys(), default=0) + 1

# CRUD operations for books

@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(list(books.values()))

@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    new_book_id = generate_id(books)
    new_book = {
        "id": new_book_id,
        "title": data["title"],
        "author": data["author"]
    }
    books[new_book_id] = new_book
    return jsonify(new_book), 201

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = books.get(book_id)
    if book is None:
        return "Book not found", 404
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    book = books.get(book_id)
    if book is None:
        return "Book not found", 404
    book["title"] = data["title"]
    book["author"] = data["author"]
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = books.pop(book_id, None)
    if book is None:
        return "Book not found", 404
    return "Book deleted", 204


##################################################### added code #####################################################

# CRUD operations for members
@app.route('/members', methods=['GET'])
def get_members():
    return jsonify(list(members.values()))

@app.route('/members', methods=['POST'])
def create_member():
    data = request.get_json()
    new_member_id = generate_id(members)
    new_member = {
        "id": new_member_id,
        "name": data["name"],
        "email": data["email"]
    }
    members[new_member_id] = new_member
    return jsonify(new_member), 201

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = members.get(member_id)
    if member is None:
        return "Member not found", 404
    return jsonify(member)

@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.get_json()
    member = members.get(member_id)
    if member is None:
        return "Member not found", 404
    member["name"] = data["name"]
    member["email"] = data["email"]
    return jsonify(member)

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = members.pop(member_id, None)
    if member is None:
        return "Member not found", 404
    return "Member deleted", 204

# CRUD operations for loans
# following end points will be able to implement loan books system  

# Get method to retrieve all loans from the loans dictionary.. 
# GET /loans
# Retrieve a list of all loans
# Response JSON structure:
# [
#     {
#         "id": <loan_id>,
#         "book_id": <book_id>,
#         "member_id": <member_id>,
#         "borrow_date": <borrow_date>,
#         "return_date": <return_date>
#     },
#     ...
# ]

# POST /loans
# Create a new loan (member borrows a book and note that into the system)
# Request JSON structure:
# {
#     "book_id": <book_id>,
#     "member_id": <member_id>,
#     "borrow_date": <borrow_date>,
#     "return_date": <return_date>      (this part might be optional based on the implementation reqirenment)
# }
# Response JSON structure:
# {
#     "id": <loan_id>,
#     "book_id": <book_id>,
#     "member_id": <member_id>,
#     "borrow_date": <borrow_date>,
#     "return_date": <return_date>
# }

# GET /loans/<int:loan_id>
# Retrieve details of a specific loan
# Response JSON structure:
# {
#     "id": <loan_id>,
#     "book_id": <book_id>,
#     "member_id": <member_id>,
#     "borrow_date": <borrow_date>,
#     "return_date": <return_date>
# }

# PUT /loans/<int:loan_id>
# Update details of a specific loan if needed in some case
# Request JSON structure:
# {
#     "book_id": <book_id>,
#     "member_id": <member_id>,
#     "borrow_date": <borrow_date>,
#     "return_date": <return_date>
# }
# Response JSON structure:
# {
#     "id": <loan_id>,
#     "book_id": <book_id>,
#     "member_id": <member_id>,
#     "borrow_date": <borrow_date>,
#     "return_date": <return_date>
# }

# DELETE /loans/<int:loan_id>
# Delete a specific loan (member returnning a book)
# Response: "Loan deleted", 204

#####################################################            #####################################################

if __name__ == '__main__':
    app.run(debug=True)
