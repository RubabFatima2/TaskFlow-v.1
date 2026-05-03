import asyncio
import httpx

async def test_api():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Login
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        resp = await client.post("/api/v1/auth/login", data=login_data)
        if resp.status_code != 200:
            print("Login failed, attempting to register...")
            reg_data = {
                "email": "testuser@example.com",
                "username": "testuser",
                "password": "testpassword123"
            }
            resp = await client.post("/api/v1/auth/register", json=reg_data)
            print("Register:", resp.status_code, resp.text)
            resp = await client.post("/api/v1/auth/login", data=login_data)
            
        print("Login status:", resp.status_code)
        cookies = resp.cookies
        
        # 2. Chat
        chat_req = {
            "message": "add task to fix the backend bug"
        }
        print("Sending chat request...")
        chat_resp = await client.post("/api/v1/chat", json=chat_req, cookies=cookies)
        print("Chat status:", chat_resp.status_code)
        print("Chat body:", chat_resp.json())

asyncio.run(test_api())
