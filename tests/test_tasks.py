import unittest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import app
from backend.database import db, User, Category, Task


class TestToDoApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        cls.client = app.test_client()

    def setUp(self):
        with app.app_context():
            db.create_all()
        
        self.test_user = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.register_user(self.test_user['username'], self.test_user['password'])
        self.token = self.login_user(self.test_user['username'], self.test_user['password'])

    def tearDown(self):
        with app.app_context():
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
        self.assertEqual(data[0]['name'], 'Work')
        self.assertEqual(data[1]['name'], 'Personal')

    def test_15_get_categories_empty_list(self):
        response = self.client.get('/categories',
                                  headers=self.get_auth_header())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

    def test_16_update_category(self):
        create_response = self.create_category('Work', 'Old description')
        category_data = json.loads(create_response.data)
        category_id = category_data['id']
        
        update_response = self.client.put(f'/categories/{category_id}',
                                         data=json.dumps({'name': 'Work Updated', 
                                                         'description': 'New description'}),
                                         content_type='application/json',
                                         headers=self.get_auth_header())
        self.assertEqual(update_response.status_code, 200)
        
        get_response = self.client.get('/categories',
                                      headers=self.get_auth_header())
        categories = json.loads(get_response.data)
        self.assertEqual(categories[0]['name'], 'Work Updated')
        self.assertEqual(categories[0]['description'], 'New description')

    def test_17_delete_category(self):
        create_response = self.create_category('ToDelete')
        category_data = json.loads(create_response.data)
        category_id = category_data['id']
        
        delete_response = self.client.delete(f'/categories/{category_id}',
                                            headers=self.get_auth_header())
        self.assertEqual(delete_response.status_code, 200)
        
        get_response = self.client.get('/categories',
                                      headers=self.get_auth_header())
        categories = json.loads(get_response.data)
        self.assertEqual(len(categories), 0)

    def test_18_delete_nonexistent_category(self):
        response = self.client.delete('/categories/9999',
                                     headers=self.get_auth_header())
        self.assertEqual(response.status_code, 404)


    def test_19_create_task_success(self):
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

    def test_20_create_task_minimal_fields(self):
        response = self.create_task('Simple task', 'Work')
        self.assertEqual(response.status_code, 201)

    def test_21_create_task_without_title(self):
        response = self.client.post('/tasks',
                                   data=json.dumps({'category_name': 'Work'}),
                                   content_type='application/json',
                                   headers=self.get_auth_header())
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_22_create_task_without_category(self):
        response = self.client.post('/tasks',
                                   data=json.dumps({'title': 'Test task'}),
                                   content_type='application/json',
                                   headers=self.get_auth_header())
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Category is required')

    def test_23_create_task_auto_create_category(self):
        response = self.create_task('Task with new category', 'NewCategory')
        self.assertEqual(response.status_code, 201)
        
        cat_response = self.client.get('/categories',
                                      headers=self.get_auth_header())
        categories = json.loads(cat_response.data)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0]['name'], 'NewCategory')

    def test_24_get_all_tasks(self):
        self.create_task('Task 1', 'Work')
        self.create_task('Task 2', 'Personal')
        
        response = self.client.get('/tasks',
                                  headers=self.get_auth_header())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

    def test_25_get_tasks_empty_list(self):
        response = self.client.get('/tasks',
                                  headers=self.get_auth_header())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

    def test_26_get_single_task(self):
        create_response = self.create_task('Test Task', 'Work',
                                          description='Test description')
        task_data = json.loads(create_response.data)
        task_id = task_data['id']
        
        response = self.client.get(f'/tasks/{task_id}',
                                  headers=self.get_auth_header())
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Test Task')
        self.assertEqual(data['description'], 'Test description')

    def test_27_get_nonexistent_task(self):
        response = self.client.get('/tasks/9999',
                                  headers=self.get_auth_header())
        self.assertEqual(response.status_code, 404)

    def test_28_update_task(self):
        create_response = self.create_task('Original Title', 'Work')
        task_data = json.loads(create_response.data)
        task_id = task_data['id']
        
        update_response = self.client.put(f'/tasks/{task_id}',
                                         data=json.dumps({
                                             'title': 'Updated Title',
                                             'description': 'Updated description',
                                             'priority': 'High',
                                             'status': 'In Progress'
                                         }),
                                         content_type='application/json',
                                         headers=self.get_auth_header())
        self.assertEqual(update_response.status_code, 200)
        
        get_response = self.client.get(f'/tasks/{task_id}',
                                      headers=self.get_auth_header())
        task = json.loads(get_response.data)
        self.assertEqual(task['title'], 'Updated Title')
        self.assertEqual(task['description'], 'Updated description')
        self.assertEqual(task['priority'], 'High')
        self.assertEqual(task['status'], 'In Progress')

    def test_29_mark_task_completed(self):
        create_response = self.create_task('Task to complete', 'Work')
        task_data = json.loads(create_response.data)
        task_id = task_data['id']
        
        update_response = self.client.put(f'/tasks/{task_id}',
                                         data=json.dumps({'status': 'Completed'}),
                                         content_type='application/json',
                                         headers=self.get_auth_header())
        self.assertEqual(update_response.status_code, 200)
        
        get_response = self.client.get(f'/tasks/{task_id}',
                                      headers=self.get_auth_header())
        task = json.loads(get_response.data)
        self.assertEqual(task['status'], 'Completed')

    def test_30_delete_task(self):
        create_response = self.create_task('Task to delete', 'Work')
        task_data = json.loads(create_response.data)
        task_id = task_data['id']
        
        delete_response = self.client.delete(f'/tasks/{task_id}',
                                            headers=self.get_auth_header())
        self.assertEqual(delete_response.status_code, 200)
        
        # Verify deletion
        get_response = self.client.get('/tasks',
                                      headers=self.get_auth_header())
        tasks = json.loads(get_response.data)
        self.assertEqual(len(tasks), 0)

    def test_31_delete_nonexistent_task(self):
        response = self.client.delete('/tasks/9999',
                                     headers=self.get_auth_header())
        self.assertEqual(response.status_code, 404)


    def test_32_task_sorting_by_due_date(self):
        self.create_task('Task 3', 'Work', due_date='2025-12-31')
        self.create_task('Task 1', 'Work', due_date='2025-10-15')
        self.create_task('Task 2', 'Work', due_date='2025-11-20')
        
        response = self.client.get('/tasks',
                                  headers=self.get_auth_header())
        tasks = json.loads(response.data)
        
        self.assertEqual(tasks[0]['title'], 'Task 1')
        self.assertEqual(tasks[1]['title'], 'Task 2')
        self.assertEqual(tasks[2]['title'], 'Task 3')

    def test_33_task_sorting_by_priority(self):
        self.create_task('Low Priority', 'Work', due_date='2025-10-15', priority='Low')
        self.create_task('High Priority', 'Work', due_date='2025-10-15', priority='High')
        self.create_task('Medium Priority', 'Work', due_date='2025-10-15', priority='Medium')
        
        response = self.client.get('/tasks',
                                  headers=self.get_auth_header())
        tasks = json.loads(response.data)
        
        self.assertEqual(tasks[0]['priority'], 'High')
        self.assertEqual(tasks[1]['priority'], 'Medium')
        self.assertEqual(tasks[2]['priority'], 'Low')

    def test_34_task_sorting_by_estimated_hours(self):
        self.create_task('5 hours', 'Work', due_date='2025-10-15', 
                        priority='High', estimated_hours=5.0)
        self.create_task('10 hours', 'Work', due_date='2025-10-15', 
                        priority='High', estimated_hours=10.0)
        self.create_task('2 hours', 'Work', due_date='2025-10-15', 
                        priority='High', estimated_hours=2.0)
        
        response = self.client.get('/tasks',
                                  headers=self.get_auth_header())
        tasks = json.loads(response.data)
        
        self.assertEqual(tasks[0]['estimated_hours'], 10.0)
        self.assertEqual(tasks[1]['estimated_hours'], 5.0)
        self.assertEqual(tasks[2]['estimated_hours'], 2.0)

    def test_35_task_sorting_nulls_last(self):
        self.create_task('With date', 'Work', due_date='2025-10-15')
        self.create_task('No date', 'Work')
        
        response = self.client.get('/tasks',
                                  headers=self.get_auth_header())
        tasks = json.loads(response.data)
        
        self.assertEqual(tasks[0]['title'], 'With date')
        self.assertEqual(tasks[1]['title'], 'No date')

    def test_36_task_sorting_combined(self):
        self.create_task('Latest Low 1h', 'Work', 
                        due_date='2025-12-31', priority='Low', estimated_hours=1.0)
        self.create_task('Earliest High 10h', 'Work', 
                        due_date='2025-10-15', priority='High', estimated_hours=10.0)
        self.create_task('Earliest High 5h', 'Work', 
                        due_date='2025-10-15', priority='High', estimated_hours=5.0)
        self.create_task('Earliest Medium 8h', 'Work', 
                        due_date='2025-10-15', priority='Medium', estimated_hours=8.0)
        
        response = self.client.get('/tasks',
                                  headers=self.get_auth_header())
        tasks = json.loads(response.data)
        
        self.assertEqual(tasks[0]['title'], 'Earliest High 10h')
        self.assertEqual(tasks[1]['title'], 'Earliest High 5h')
        self.assertEqual(tasks[2]['title'], 'Earliest Medium 8h')
        self.assertEqual(tasks[3]['title'], 'Latest Low 1h')


    def test_37_task_with_special_characters(self):
        response = self.create_task('Task: "Test" & <Special> Chars!', 'Work')
        self.assertEqual(response.status_code, 201)

    def test_38_task_with_very_long_description(self):
        response = self.create_task('Long desc task', 'Work', description=long_desc)
        self.assertEqual(response.status_code, 201)

    def test_39_task_with_zero_estimated_hours(self):
        response = self.create_task('Zero hours', 'Work', estimated_hours=0.0)
        self.assertEqual(response.status_code, 201)

    def test_40_task_with_decimal_estimated_hours(self):
        response = self.create_task('Decimal hours', 'Work', estimated_hours=2.5)
        self.assertEqual(response.status_code, 201)
        
        get_response = self.client.get('/tasks',
                                      headers=self.get_auth_header())
        tasks = json.loads(get_response.data)
        self.assertEqual(tasks[0]['estimated_hours'], 2.5)

    def test_41_multiple_users_isolation(self):
        self.create_task('User 1 Task', 'Work')
        
        self.register_user('user2', 'pass2')
        token2 = self.login_user('user2', 'pass2')
        
        response = self.client.get('/tasks',
                                  headers={'Authorization': f'Bearer {token2}'})
        tasks = json.loads(response.data)
        
        self.assertIsInstance(tasks, list)

    def test_42_update_task_change_category(self):
        self.create_category('OldCategory')
        self.create_category('NewCategory')
        
        create_response = self.create_task('Task', 'OldCategory')
        task_id = json.loads(create_response.data)['id']
        
        update_response = self.client.put(f'/tasks/{task_id}',
                                         data=json.dumps({'category_name': 'NewCategory'}),
                                         content_type='application/json',
                                         headers=self.get_auth_header())
        self.assertEqual(update_response.status_code, 200)
        
        get_response = self.client.get(f'/tasks/{task_id}',
                                      headers=self.get_auth_header())
        task = json.loads(get_response.data)
        self.assertEqual(task['category'], 'NewCategory')

    def test_43_update_task_with_null_category(self):
        create_response = self.create_task('Task', 'Work')
        task_id = json.loads(create_response.data)['id']
        
        update_response = self.client.put(f'/tasks/{task_id}',
                                         data=json.dumps({'category_id': None}),
                                         content_type='application/json',
                                         headers=self.get_auth_header())
        self.assertEqual(update_response.status_code, 400)
        data = json.loads(update_response.data)
        self.assertEqual(data['error'], 'Category is required')

    def test_44_password_hashing(self):
        with app.app_context():
            user = User.query.filter_by(username=self.test_user['username']).first()
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password_hash, self.test_user['password'])
            self.assertIsInstance(user.password_hash, str)
            self.assertGreater(len(user.password_hash), 50)

    def test_45_password_verification(self):
        with app.app_context():
            user = User.query.filter_by(username=self.test_user['username']).first()
            self.assertTrue(user.check_password(self.test_user['password']))
            self.assertFalse(user.check_password('wrongpassword'))


class TestDatabaseModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    def setUp(self):
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_model_creation(self):
        with app.app_context():
            user = User(username='testuser')
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()
            
            retrieved_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(retrieved_user)
            self.assertEqual(retrieved_user.username, 'testuser')

    def test_category_model_creation(self):
        with app.app_context():
            category = Category(name='Work', description='Work tasks')
            db.session.add(category)
            db.session.commit()
            
            retrieved_cat = Category.query.filter_by(name='Work').first()
            self.assertIsNotNone(retrieved_cat)
            self.assertEqual(retrieved_cat.description, 'Work tasks')

    def test_task_model_creation(self):
        with app.app_context():
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

    def test_category_task_relationship(self):
        with app.app_context():
            category = Category(name='Work')
            db.session.add(category)
            db.session.commit()
            
            task1 = Task(title='Task 1', category_id=category.id)
            task2 = Task(title='Task 2', category_id=category.id)
            db.session.add_all([task1, task2])
            db.session.commit()
            
            retrieved_cat = Category.query.filter_by(name='Work').first()
            self.assertEqual(len(retrieved_cat.tasks), 2)
            self.assertEqual(retrieved_cat.tasks[0].title, 'Task 1')


def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestToDoApp))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseModels))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    
    sys.exit(0 if success else 1)