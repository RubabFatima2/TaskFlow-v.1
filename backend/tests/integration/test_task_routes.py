import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTaskRoutes:
    """Integration tests for task routes"""

    async def test_create_task_success(self, client, test_user):
        """Test POST /api/v1/tasks with valid data"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Create task
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["completed"] is False
        assert data["user_id"] == test_user["id"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_task_without_description(self, client, test_user):
        """Test creating task without description"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Create task without description
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "No Description Task"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "No Description Task"
        assert data["description"] is None

    async def test_create_task_unauthenticated(self, client):
        """Test creating task without authentication returns 401"""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Unauthorized Task"}
        )

        assert response.status_code == 401

    async def test_create_task_empty_title(self, client, test_user):
        """Test creating task with empty title returns 422"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Try to create task with empty title
        response = await client.post(
            "/api/v1/tasks",
            json={"title": ""}
        )

        assert response.status_code == 422

    async def test_create_task_title_too_long(self, client, test_user):
        """Test creating task with title > 200 chars returns 422"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Try to create task with long title
        long_title = "a" * 201
        response = await client.post(
            "/api/v1/tasks",
            json={"title": long_title}
        )

        assert response.status_code == 422

    async def test_get_all_tasks(self, client, test_user):
        """Test GET /api/v1/tasks returns all user tasks"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Create multiple tasks
        await client.post("/api/v1/tasks", json={"title": "Task 1"})
        await client.post("/api/v1/tasks", json={"title": "Task 2"})
        await client.post("/api/v1/tasks", json={"title": "Task 3"})

        # Get all tasks
        response = await client.get("/api/v1/tasks")

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert data["total"] == 3
        assert len(data["tasks"]) == 3
        assert all(task["user_id"] == test_user["id"] for task in data["tasks"])

    async def test_get_all_tasks_unauthenticated(self, client):
        """Test getting tasks without authentication returns 401"""
        response = await client.get("/api/v1/tasks")

        assert response.status_code == 401

    async def test_get_all_tasks_empty_list(self, client, test_user):
        """Test getting tasks when user has no tasks"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Get all tasks
        response = await client.get("/api/v1/tasks")

        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["total"] == 0

    async def test_get_task_by_id(self, client, test_user):
        """Test GET /api/v1/tasks/{id} returns specific task"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Specific Task"}
        )
        task_id = create_response.json()["id"]

        # Get task by ID
        response = await client.get(f"/api/v1/tasks/{task_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Specific Task"

    async def test_get_task_by_id_not_found(self, client, test_user):
        """Test getting non-existent task returns 404"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Try to get non-existent task
        response = await client.get("/api/v1/tasks/99999")

        assert response.status_code == 404

    async def test_get_task_by_id_unauthenticated(self, client):
        """Test getting task without authentication returns 401"""
        response = await client.get("/api/v1/tasks/1")

        assert response.status_code == 401

    async def test_update_task_title(self, client, test_user):
        """Test PUT /api/v1/tasks/{id} updates task title"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Original Title"}
        )
        task_id = create_response.json()["id"]

        # Update task
        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Updated Title"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["id"] == task_id

    async def test_update_task_completed_status(self, client, test_user):
        """Test updating task completed status"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Complete Me"}
        )
        task_id = create_response.json()["id"]

        # Mark as completed
        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={"completed": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    async def test_update_task_multiple_fields(self, client, test_user):
        """Test updating multiple task fields at once"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Original", "description": "Original Desc"}
        )
        task_id = create_response.json()["id"]

        # Update multiple fields
        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={
                "title": "Updated",
                "description": "Updated Desc",
                "completed": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"
        assert data["description"] == "Updated Desc"
        assert data["completed"] is True

    async def test_update_task_not_found(self, client, test_user):
        """Test updating non-existent task returns 404"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Try to update non-existent task
        response = await client.put(
            "/api/v1/tasks/99999",
            json={"title": "Updated"}
        )

        assert response.status_code == 404

    async def test_update_task_unauthenticated(self, client):
        """Test updating task without authentication returns 401"""
        response = await client.put(
            "/api/v1/tasks/1",
            json={"title": "Updated"}
        )

        assert response.status_code == 401

    async def test_delete_task_success(self, client, test_user):
        """Test DELETE /api/v1/tasks/{id} deletes task"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Delete Me"}
        )
        task_id = create_response.json()["id"]

        # Delete task
        response = await client.delete(f"/api/v1/tasks/{task_id}")

        assert response.status_code == 204

        # Verify task is deleted
        get_response = await client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == 404

    async def test_delete_task_not_found(self, client, test_user):
        """Test deleting non-existent task returns 404"""
        # Login first
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # Try to delete non-existent task
        response = await client.delete("/api/v1/tasks/99999")

        assert response.status_code == 404

    async def test_delete_task_unauthenticated(self, client):
        """Test deleting task without authentication returns 401"""
        response = await client.delete("/api/v1/tasks/1")

        assert response.status_code == 401

    async def test_user_data_isolation(self, client):
        """Test that users can only access their own tasks"""
        # Register and login user 1
        await client.post(
            "/api/v1/auth/register",
            json={"email": "user1@example.com", "password": "password123"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "user1@example.com", "password": "password123"}
        )

        # Create task as user 1
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "User 1 Task"}
        )
        task_id = create_response.json()["id"]

        # Logout user 1
        await client.post("/api/v1/auth/logout")

        # Register and login user 2
        await client.post(
            "/api/v1/auth/register",
            json={"email": "user2@example.com", "password": "password123"}
        )
        await client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "password123"}
        )

        # Try to access user 1's task as user 2
        response = await client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 404  # Should not find task

        # Try to update user 1's task as user 2
        update_response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Hacked"}
        )
        assert update_response.status_code == 404

        # Try to delete user 1's task as user 2
        delete_response = await client.delete(f"/api/v1/tasks/{task_id}")
        assert delete_response.status_code == 404

    async def test_task_crud_flow_end_to_end(self, client, test_user):
        """Test complete task CRUD flow"""
        # Login
        await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "testpassword123"
            }
        )

        # 1. Create task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "CRUD Test Task", "description": "Testing CRUD"}
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # 2. Read task
        read_response = await client.get(f"/api/v1/tasks/{task_id}")
        assert read_response.status_code == 200
        assert read_response.json()["title"] == "CRUD Test Task"

        # 3. Update task
        update_response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Updated CRUD Task", "completed": True}
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated CRUD Task"
        assert update_response.json()["completed"] is True

        # 4. Delete task
        delete_response = await client.delete(f"/api/v1/tasks/{task_id}")
        assert delete_response.status_code == 204

        # 5. Verify deletion
        verify_response = await client.get(f"/api/v1/tasks/{task_id}")
        assert verify_response.status_code == 404
