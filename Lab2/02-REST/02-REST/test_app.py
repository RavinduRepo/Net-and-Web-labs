import unittest
import json
from app import app

class LibraryAppTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_get_books(self):
        response = self.app.get('/books')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIsInstance(data, list)

    def test_get_nonexistent_book(self):
        response = self.app.get('/books/999')
        self.assertEqual(response.status_code, 404)

    def test_create_and_delete_book(self):
        # Create a new book
        new_book_data = {"title": "Test Book", "author": "Test Author"}
        response = self.app.post('/books', json=new_book_data)
        self.assertEqual(response.status_code, 201)
        created_book = json.loads(response.get_data(as_text=True))

        # Retrieve the created book
        response = self.app.get(f'/books/{created_book["id"]}')
        self.assertEqual(response.status_code, 200)

        # Delete the created book
        response = self.app.delete(f'/books/{created_book["id"]}')
        self.assertEqual(response.status_code, 204)

        # Verify that the book is deleted
        response = self.app.get(f'/books/{created_book["id"]}')
        self.assertEqual(response.status_code, 404)

##################################################### added code #####################################################

    # Added a test case for updating a book  
    def test_get_members(self): 

        response = self.app.get('/members')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIsInstance(data, list)

    def test_get_nonexistent_member(self):
        response = self.app.get('/members/999')
        self.assertEqual(response.status_code, 404)

    def test_create_and_delete_member(self):
        # Create a new member 
        new_member_data = {"name": "Test Member", "email": "testmember@example.com"}
        response = self.app.post('/members', json=new_member_data)
        self.assertEqual(response.status_code, 201)
        created_member = json.loads(response.get_data(as_text=True))

        # Retrieve the created member
        response = self.app.get(f'/members/{created_member["id"]}')
        self.assertEqual(response.status_code, 200)

        # Delete the created member
        response = self.app.delete(f'/members/{created_member["id"]}')
        self.assertEqual(response.status_code, 204)

        # Verify that the member is deleted
        response = self.app.get(f'/members/{created_member["id"]}')
        self.assertEqual(response.status_code, 404)

    def test_update_member(self):
        # Create a new member
        new_member_data = {"name": "Test Member", "email": "testmember@example.com"}
        response = self.app.post('/members', json=new_member_data)
        self.assertEqual(response.status_code, 201)
        created_member = json.loads(response.get_data(as_text=True))

        # Update the created member
        updated_member_data = {"name": "Updated Test Member", "email": "updatedtestmember@example.com"}
        response = self.app.put(f'/members/{created_member["id"]}', json=updated_member_data)
        self.assertEqual(response.status_code, 200)
        updated_member = json.loads(response.get_data(as_text=True))
        self.assertEqual(updated_member["name"], "Updated Test Member")
        self.assertEqual(updated_member["email"], "updatedtestmember@example.com")

        # Retrieve the updated member
        response = self.app.get(f'/members/{created_member["id"]}')
        self.assertEqual(response.status_code, 200)
        retrieved_member = json.loads(response.get_data(as_text=True))
        self.assertEqual(retrieved_member["name"], "Updated Test Member")
        self.assertEqual(retrieved_member["email"], "updatedtestmember@example.com")

        # Delete the created member
        response = self.app.delete(f'/members/{created_member["id"]}')
        self.assertEqual(response.status_code, 204)
        
#####################################################            #####################################################

if __name__ == '__main__':
    unittest.main()
