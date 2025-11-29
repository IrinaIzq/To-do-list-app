"""
Integration tests for API endpoints.
Tests complete request-response cycles through the API.
"""
import pytest
import json


class TestAuthenticationEndpoints:
    """Test authentication API endpoints."""
    
    def test_register_and_login_flow(self, client):
        """Test complete registration and login flow."""
        # Register new user
        register_response = client.post('/register',
            json={'username': 'newuser', 'password': 'password123'}
        )
        assert register_response.status_code == 201
        assert b'User created successfully' in register_response.data
        
        # Login with new user
        login_response = client.post('/login',
            json={'username': 'newuser', 'password': 'password123'}
        )
        assert login_response.status_code == 200
        data = json.loads(login_response.data)
        assert 'token' in data
        assert len(data['token']) > 0
    
    def test_login_with_invalid_credentials(self, client):
        """Test login with wrong credentials."""
        response = client.post('/login',
            json={'username': 'nonexistent', 'password': 'wrong'}
        )
        assert response.status_code == 401
        assert b'Invalid credentials' in response.data
    
    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without authentication."""
        response = client.get('/tasks')
        assert response.status_code == 401
        assert b'Token is missing' in response.data
    
    def test_access_with_invalid_token(self, client):
        """Test accessing with malformed token."""
        response = client.get('/tasks',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        assert response.status_code == 401


class TestCategoryEndpoints:
    """Test category API endpoints."""
    
    def test_create_category(self, client, auth_headers):
        """Test creating a category."""
        response = client.post('/categories',
            json={'name': 'Work', 'description': 'Work tasks'},
            headers=auth_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Work'
        assert data['description'] == 'Work tasks'
        assert 'id' in data
    
    def test_get_all_categories(self, client, auth_headers, test_category):
        """Test retrieving all categories."""
        response = client.get('/categories', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]['name'] == test_category.name
    
    def test_update_category(self, client, auth_headers, test_category):
        """Test updating a category."""
        response = client.put(f'/categories/{test_category.id}',
            json={'name': 'Updated Name', 'description': 'Updated desc'},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify update
        get_response = client.get('/categories', headers=auth_headers)
        categories = json.loads(get_response.data)
        updated = next(c for c in categories if c['id'] == test_category.id)
        assert updated['name'] == 'Updated Name'
    
    def test_delete_category(self, client, auth_headers, test_category):
        """Test deleting a category."""
        response = client.delete(f'/categories/{test_category.id}',
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get('/categories', headers=auth_headers)
        categories = json.loads(get_response.data)
        assert not any(c['id'] == test_category.id for c in categories)
    
    def test_create_duplicate_category(self, client, auth_headers, test_category):
        """Test creating category with duplicate name."""
        response = client.post('/categories',
            json={'name': test_category.name, 'description': 'Duplicate'},
            headers=auth_headers
        )
        assert response.status_code == 400
        assert b'already exists' in response.data


class TestTaskEndpoints:
    """Test task API endpoints."""
    
    def test_create_task(self, client, auth_headers, test_category):
        """Test creating a task."""
        response = client.post('/tasks',
            json={
                'title': 'New Task',
                'description': 'Task description',
                'category_id': test_category.id,
                'priority': 'High',
                'estimated_hours': 5.0,
                'due_date': '2025-12-31'
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'id' in data
        assert 'message' in data
    
    def test_create_task_with_auto_category(self, client, auth_headers):
        """Test creating task - note: auto-category not implemented, so this should fail."""
        response = client.post('/tasks',
            json={
                'title': 'Task with new category',
                'category_name': 'Auto Category'
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert b'category is required' in response.data
    
    def test_get_all_tasks(self, client, auth_headers, multiple_tasks):
        """Test retrieving all tasks."""
        response = client.get('/tasks', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 3
    
    def test_tasks_sorted_correctly(self, client, auth_headers, multiple_tasks):
        """Test that tasks are sorted by due date, priority, estimated hours."""
        response = client.get('/tasks', headers=auth_headers)
        tasks = json.loads(response.data)
        
        # First task should be high priority with earliest date
        assert tasks[0]['priority'] == 'High'
        assert tasks[0]['due_date'] == '2025-12-01T00:00:00'
        assert tasks[0]['estimated_hours'] == 10
        
        # Second should be medium priority with same date
        assert tasks[1]['priority'] == 'Medium'
        assert tasks[1]['due_date'] == '2025-12-01T00:00:00'
        
        # Third should be low priority with later date
        assert tasks[2]['priority'] == 'Low'
        assert tasks[2]['due_date'] == '2025-12-15T00:00:00'
    
    def test_get_single_task(self, client, auth_headers, test_task):
        """Test retrieving a single task."""
        response = client.get(f'/tasks/{test_task.id}', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_task.id
        assert data['title'] == test_task.title
    
    def test_update_task(self, client, auth_headers, test_task):
        """Test updating a task."""
        response = client.put(f'/tasks/{test_task.id}',
            json={
                'title': 'Updated Title',
                'status': 'Completed',
                'priority': 'Low'
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify update
        get_response = client.get(f'/tasks/{test_task.id}', headers=auth_headers)
        task = json.loads(get_response.data)
        assert task['title'] == 'Updated Title'
        assert task['status'] == 'Completed'
        assert task['priority'] == 'Low'
    
    def test_delete_task(self, client, auth_headers, test_task):
        """Test deleting a task."""
        response = client.delete(f'/tasks/{test_task.id}', headers=auth_headers)
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get(f'/tasks/{test_task.id}', headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_create_task_without_title(self, client, auth_headers, test_category):
        """Test creating task without required title."""
        response = client.post('/tasks',
            json={'category_id': test_category.id, 'priority': 'High', 'hours': 5},
            headers=auth_headers
        )
        assert response.status_code == 400
        assert b'title required' in response.data
    
    def test_create_task_without_category(self, client, auth_headers):
        """Test creating task without required category."""
        response = client.post('/tasks',
            json={'title': 'No category task'},
            headers=auth_headers
        )
        assert response.status_code == 400
        assert b'category is required' in response.data.lower()
    
    def test_create_task_with_invalid_priority(self, client, auth_headers, test_category):
        """Test creating task with invalid priority."""
        response = client.post('/tasks',
            json={
                'title': 'Task',
                'category_id': test_category.id,
                'priority': 'Invalid',  # This will be mapped to default (Medium = 2)
                'hours': 5
            },
            headers=auth_headers
        )
        assert response.status_code == 201
    
    def test_create_task_with_negative_hours(self, client, auth_headers, test_category):
        """Test creating task with negative estimated hours."""
        response = client.post('/tasks',
            json={
                'title': 'Task',
                'category_id': test_category.id,
                'estimated_hours': -5.0,
                'priority': 'High'
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert b'non-negative' in response.data.lower()


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns proper status."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] in ['healthy', 'degraded']
        assert 'timestamp' in data
        assert 'version' in data
        assert 'database' in data


class TestCompleteWorkflow:
    """Test complete user workflows."""
    
    def test_complete_task_management_workflow(self, client):
        """Test complete workflow: register, login, create category, create task, update, delete."""
        # 1. Register user
        client.post('/register',
            json={'username': 'workflowuser', 'password': 'pass123'}
        )
        
        # 2. Login
        login_response = client.post('/login',
            json={'username': 'workflowuser', 'password': 'pass123'}
        )
        token = json.loads(login_response.data)['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 3. Create category
        cat_response = client.post('/categories',
            json={'name': 'Project', 'description': 'Project tasks'},
            headers=headers
        )
        category_id = json.loads(cat_response.data)['id']
        
        # 4. Create task
        task_response = client.post('/tasks',
            json={
                'title': 'Build feature',
                'category_id': category_id,
                'priority': 'High',
                'estimated_hours': 8.0
            },
            headers=headers
        )
        data = json.loads(task_response.data)
        assert 'id' in data
        task_id = data['id']
        
        # 5. Update task status
        client.put(f'/tasks/{task_id}',
            json={'status': 'In Progress'},
            headers=headers
        )
        
        # 6. Verify task state
        get_response = client.get(f'/tasks/{task_id}', headers=headers)
        task = json.loads(get_response.data)
        assert task['status'] == 'In Progress'
        assert task['priority'] == 'High'
        
        # 7. Complete task
        client.put(f'/tasks/{task_id}',
            json={'status': 'Completed'},
            headers=headers
        )
        
        # 8. Verify completion
        final_response = client.get(f'/tasks/{task_id}', headers=headers)
        final_task = json.loads(final_response.data)
        assert final_task['status'] == 'Completed'