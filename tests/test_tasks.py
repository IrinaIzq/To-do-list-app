import unittest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database import db, User, Category, Task


class TestToDoApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        with self.app.app_context():
            db.create_all()
        
        self.test_user = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.register_user(self.test_user['username'], self.test_user['password'])
        self.token = self.login_user(self.test_user['username'], self.test_user['password'])

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def register_user(self, username, password):
        response = self.client.post('/register',
                                    data=json.dumps({'username': username, 'password': password}),
                                    content_type='application/json')
        return response

    def login_user(self, username, password):
        response = self.client.post('/login',
                                    data=json.dumps({'username': username, 'password': password}),
                                    content_type='application/json')
        data = json.loads(response.data)
        return data.get('token')

    def get_auth_header(self):
        return {'Authorization': f'Bearer {self.token}'}

    def create_category(self, name, description=None):
        category_data = {'name': name}
        if description:
            category_data['description'] = description
        
        response = self.client.post('/categories',
                                   data=json.dumps(category_data),
                                   content_type='application/json',
                                   headers=self.get_auth_header())
        return response

    def create_task(self, title, category_name, **kwargs):
        task_data = {
            'title': title,
            'category_name': category_name,
            **kwargs
        }
        
        response = self.client.post('/tasks',
                                   data=json.dumps(task_data),
                                   content_type='application/json',
                                   headers=self.get_auth_header())
        return response

    def test_01_register_user_success(self):
        response = self.register_user('newuser', 'newpass123')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User created successfully')

    def test_02_register_duplicate_user(self):
        response = self.register_user(self.test_user['username'], 'anotherpass')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User already exists')

    def test_03_register_missing_username(self):
        response = self.client.post('/register',
                                   data=json.dumps({'password': 'testpass'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_04_register_missing_password(self):
        response = self.client.post('/register',
                                   data=json.dumps({'username': 'testuser'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_05_login_success(self):
        token = self.login_user(self.test_user['username'], self.test_user['password'])
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_06_login_wrong_password(self):
        response = self.client.post('/login',
                                   data=json.dumps({'username': self.test_user['username'], 
                                                   'password': 'wrongpass'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_07_login_nonexistent_user(self):
        response = self.client.post('/login',
                                   data=json.dumps({'username': 'nonexistent', 
                                                   'password': 'pass123'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_08_access_protected_route_without_token(self):
        response = self.client.get('/categories')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_09_access_protected_route_invalid_token(self):
        response = self.client.get('/categories',
                                  headers={'Authorization': 'Bearer invalidtoken123'})
        self.assertEqual(response.status_code, 401)

    def test_10_create_category_success(self):
        response = self.create_category('Work', 'Work-related tasks')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Work')
        self.assertEqual(data['description'], 'Work-related tasks')
        self.assertIn('id', data)

    def test_11_create_category_without_description(self):
        response = self.create_category('Personal')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Personal')

    def test_12_create_category_missing_name(self):
        response = self.client.post('/categories',
                                   data=json.dumps({'description': 'No name'}),
                                   content_type='application/json',
                                   headers=self.get_auth_header())
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_13_create_duplicate_category(self):
        self.create_category('Work')
        response = self.create_category('Work')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Category already exists')

    def test_14_get_all_categories(self):
        self.create_category('Work', 'Work tasks')
        self.create_category('Personal', 'Personal tasks')
        
        response = self.client.get('/categories',
                                  headers=self.get_auth_header())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

    def test_15_create_task_success(self):
        self.create_category('Work')
        response = self.create_task('Complete report', 'Work',
                                   description='Finish Q4 report',
                                   due_date='2025-12-31',
                                   estimated_hours=5.0,
                                   priority='High')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertEqual(data['message'], 'Task created')

    def test_16_get_all_tasks(self):
        self.create_task('Task 1', 'Work')
        self.create_task('Task 2', 'Personal')
        
        response = self.client.get('/tasks',
                                  headers=self.get_auth_header())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)


class TestDatabaseModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    def setUp(self):
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_model_creation(self):
        with self.app.app_context():
            user = User(username='testuser')
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()
            
            retrieved_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(retrieved_user)
            self.assertEqual(retrieved_user.username, 'testuser')

    def test_category_model_creation(self):
        with self.app.app_context():
            category = Category(name='Work', description='Work tasks')
            db.session.add(category)
            db.session.commit()
            
            retrieved_cat = Category.query.filter_by(name='Work').first()
            self.assertIsNotNone(retrieved_cat)
            self.assertEqual(retrieved_cat.description, 'Work tasks')

    def test_task_model_creation(self):
        with self.app.app_context():
            category = Category(name='Work')
            db.session.add(category)
            db.session.commit()
            
            task = Task(
                title='Test Task',
                description='Test description',
                category_id=category.id,
                estimated_hours=5.0,
                due_date='2025-12-31',
                priority='High',
                status='Pending'
            )
            db.session.add(task)
            db.session.commit()
            
            retrieved_task = Task.query.filter_by(title='Test Task').first()
            self.assertIsNotNone(retrieved_task)
            self.assertEqual(retrieved_task.priority, 'High')


if __name__ == '__main__':
    unittest.main()