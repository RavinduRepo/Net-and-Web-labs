#!/bin/sh
# Add a new book
curl -X POST -H "Content-Type: application/json" \
    -d '{"title": "New Book Title", "author": "A. B. C"}' http://localhost:5000/books

# List all books
curl http://127.0.0.1:5000/books

# List details of book id 1
curl http://127.0.0.1:5000/books/1

# Update a book's title and author
curl -X PUT -H "Content-Type: application/json" \
    -d '{"title": "Updated book Title", "author": "X. Y. Z"}' http://localhost:5000/books/1

# Delete a book
curl -X DELETE http://localhost:5000/books/1