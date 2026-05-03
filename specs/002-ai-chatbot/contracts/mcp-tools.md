# MCP Tools Contract

**Feature**: 002-ai-chatbot  
**Date**: 2026-04-25  
**Purpose**: Define MCP tool schemas for Gemini function calling

---

## Overview

Five MCP tools provide task management operations for the AI chatbot. All tools:
- Reuse existing Task model from Phase 2
- Automatically receive `user_id` from JWT token (injected by agent service)
- Return structured responses with `success` boolean and data/error fields
- Validate inputs using Pydantic models
- Enforce user-level data isolation

---

## Tool 1: add_task

**Purpose**: Create a new task for the authenticated user

**Function Signature**:
```python
async def add_task(user_id: str, title: str, description: str = "") -> dict
```

**Gemini Function Schema**:
```json
{
  "name": "add_task",
  "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something.",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "User ID from JWT token (automatically injected)"
      },
      "title": {
        "type": "string",
        "description": "Task title extracted from user message (1-200 characters)"
      },
      "description": {
        "type": "string",
        "description": "Optional task description with additional details"
      }
    },
    "required": ["user_id", "title"]
  }
}
```

**Input Validation**:
- `title`: 1-200 characters, non-empty
- `description`: 0-2000 characters, optional

**Success Response**:
```json
{
  "success": true,
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "completed": false,
    "created_at": "ISO 8601 datetime"
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

**Example Usage**:
```
User: "add buy groceries"
Tool Call: add_task(user_id="user_123", title="buy groceries")
Response: {"success": true, "task": {...}}
```

---

## Tool 2: list_tasks

**Purpose**: Retrieve tasks for the authenticated user with optional status filter

**Function Signature**:
```python
async def list_tasks(user_id: str, status: str = "all") -> dict
```

**Gemini Function Schema**:
```json
{
  "name": "list_tasks",
  "description": "List the user's tasks. Use this when the user wants to see, view, or check their tasks. Can filter by status (all, pending, completed).",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "User ID from JWT token (automatically injected)"
      },
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "description": "Filter tasks by completion status. Default: all"
      }
    },
    "required": ["user_id"]
  }
}
```

**Input Validation**:
- `status`: Must be "all", "pending", or "completed"

**Success Response**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "completed": boolean,
      "created_at": "ISO 8601 datetime",
      "updated_at": "ISO 8601 datetime"
    }
  ],
  "count": integer
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message"
}
```

**Example Usage**:
```
User: "show my pending tasks"
Tool Call: list_tasks(user_id="user_123", status="pending")
Response: {"success": true, "tasks": [...], "count": 3}
```

---

## Tool 3: complete_task

**Purpose**: Mark a task as completed

**Function Signature**:
```python
async def complete_task(user_id: str, task_id: str) -> dict
```

**Gemini Function Schema**:
```json
{
  "name": "complete_task",
  "description": "Mark a task as completed. Use this when the user says they finished, completed, or are done with a task.",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "User ID from JWT token (automatically injected)"
      },
      "task_id": {
        "type": "string",
        "description": "ID of the task to mark complete. Must match a task from list_tasks."
      }
    },
    "required": ["user_id", "task_id"]
  }
}
```

**Input Validation**:
- `task_id`: Must be valid UUID
- Task must exist and belong to user

**Success Response**:
```json
{
  "success": true,
  "task": {
    "id": "uuid",
    "title": "string",
    "completed": true,
    "updated_at": "ISO 8601 datetime"
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Task not found" | "Task does not belong to user"
}
```

**Example Usage**:
```
User: "mark buy groceries as done"
Tool Call: list_tasks() -> find task_id for "buy groceries"
Tool Call: complete_task(user_id="user_123", task_id="task_456")
Response: {"success": true, "task": {...}}
```

---

## Tool 4: update_task

**Purpose**: Update task title and/or description

**Function Signature**:
```python
async def update_task(user_id: str, task_id: str, title: str = None, description: str = None) -> dict
```

**Gemini Function Schema**:
```json
{
  "name": "update_task",
  "description": "Update a task's title or description. Use this when the user wants to change, modify, or update task details. At least one of title or description must be provided.",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "User ID from JWT token (automatically injected)"
      },
      "task_id": {
        "type": "string",
        "description": "ID of the task to update"
      },
      "title": {
        "type": "string",
        "description": "New task title (1-200 characters, optional)"
      },
      "description": {
        "type": "string",
        "description": "New task description (0-2000 characters, optional)"
      }
    },
    "required": ["user_id", "task_id"]
  }
}
```

**Input Validation**:
- `task_id`: Must be valid UUID
- `title`: 1-200 characters if provided
- `description`: 0-2000 characters if provided
- At least one of `title` or `description` must be provided

**Success Response**:
```json
{
  "success": true,
  "task": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "completed": boolean,
    "updated_at": "ISO 8601 datetime"
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Task not found" | "At least one field must be updated"
}
```

**Example Usage**:
```
User: "change groceries to buy milk and eggs"
Tool Call: list_tasks() -> find task_id for "groceries"
Tool Call: update_task(user_id="user_123", task_id="task_456", title="buy milk and eggs")
Response: {"success": true, "task": {...}}
```

---

## Tool 5: delete_task

**Purpose**: Permanently delete a task

**Function Signature**:
```python
async def delete_task(user_id: str, task_id: str) -> dict
```

**Gemini Function Schema**:
```json
{
  "name": "delete_task",
  "description": "Permanently delete a task. Use this when the user wants to remove, delete, or cancel a task.",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "User ID from JWT token (automatically injected)"
      },
      "task_id": {
        "type": "string",
        "description": "ID of the task to delete"
      }
    },
    "required": ["user_id", "task_id"]
  }
}
```

**Input Validation**:
- `task_id`: Must be valid UUID
- Task must exist and belong to user

**Success Response**:
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Task not found" | "Task does not belong to user"
}
```

**Example Usage**:
```
User: "delete the groceries task"
Tool Call: list_tasks() -> find task_id for "groceries"
Tool Call: delete_task(user_id="user_123", task_id="task_456")
Response: {"success": true, "message": "Task deleted successfully"}
```

---

## Common Patterns

### Multi-Step Tool Calls
When user references a task by title (not ID), the agent must:
1. Call `list_tasks()` to get all tasks
2. Match task title from user message
3. Extract `task_id` from matched task
4. Call target tool with `task_id`

**Example**:
```
User: "mark buy groceries as done"

Step 1: list_tasks(user_id="user_123", status="all")
Result: [{"id": "task_456", "title": "buy groceries", ...}, ...]

Step 2: Match "buy groceries" -> task_id = "task_456"

Step 3: complete_task(user_id="user_123", task_id="task_456")
Result: {"success": true, ...}
```

### Ambiguous Task References
When multiple tasks match user's description:
1. Call `list_tasks()` to get matching tasks
2. Return list to user and ask for clarification
3. Wait for user to specify which task

**Example**:
```
User: "delete the report task"

Step 1: list_tasks() -> finds 3 tasks with "report" in title

Response: "I found 3 tasks with 'report' in the title:
1. Write quarterly report
2. Review report draft
3. Submit report to manager

Which one would you like to delete?"
```

### Error Handling
When tool execution fails:
1. Tool returns `{"success": false, "error": "..."}`
2. Agent includes error in natural language response
3. Agent suggests corrective action

**Example**:
```
Tool Call: complete_task(user_id="user_123", task_id="invalid_id")
Result: {"success": false, "error": "Task not found"}

Response: "I couldn't find that task. Would you like to see your current tasks?"
```

---

## Security Considerations

### User ID Injection
- `user_id` is ALWAYS injected by agent service from JWT token
- Tools MUST validate that task belongs to user before operations
- Never trust `user_id` from tool input directly

### Authorization Checks
```python
# In each tool implementation
task = await db.get_task(task_id)
if task.user_id != user_id:
    return {"success": false, "error": "Task does not belong to user"}
```

### Input Sanitization
- All string inputs validated by Pydantic
- No HTML/script injection risk (plain text only)
- Length limits enforced

---

## Testing Strategy

### Unit Tests
- Test each tool with valid inputs
- Test each tool with invalid inputs (validation errors)
- Test authorization (user accessing another user's task)
- Test edge cases (empty title, max length, special characters)

### Integration Tests
- Test tool execution through agent service
- Test multi-step tool calls (list + complete)
- Test error propagation to user
- Test concurrent tool calls

### Contract Tests
- Verify tool schemas match Gemini function calling format
- Verify tool responses match documented schemas
- Verify error responses are consistent

---

**MCP Tools Contract Complete**: Ready for quickstart guide generation.
