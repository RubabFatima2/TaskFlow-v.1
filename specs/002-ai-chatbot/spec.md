# Feature Specification: AI-Powered Todo Chatbot (Phase 3)

**Feature Branch**: `002-ai-chatbot`  
**Created**: 2026-04-25  
**Status**: Draft  
**Input**: User description: "Project:Evoluton of Todo-Phase 3(AI Chatbot) Evovng from : Phase 2(Full Stack Web App Akready built)  Exisiting codebase to build on p of: -backendmodeks.py(Task mdeks already exists). - backend/d.py(Neon DB conection already esxists). backend/routes/(Task CRUD routes already exists).-backend /utils/auth.py(JWT middleware alreqdy exsts).-Fronted/(Next.js a[p already exists).  --STACK ADDED IN PHASE 3:-OpenAI AGENTS SDK(agent loop+ tool orcheatration) -Gemini API(gemini-2.0 flash) as LLM . - Official MCP Python SDK for tools, -OpenAI Chatkit for CHAT UI. -Conversation + Message tables(NEW) Spec fles returnes from any code. Do not use OPENAI GT MODELS. :-specs/featured/chatbbot.md,-specs/api/mcp-toold.md. specs/api/chat_endpoint.md.-specs/databse/schema.ms(UPDATE-ADD CONVERSTAION+ MESSAAGE). -specs/architectre.md(UPFATE- add MCP +Gemini LAYER. Each sec must contain:- ser stres, Acceptance criters, Edge cases, Validation rules, Dta contracts. --MCO ROOLA(5 requirwed, all reuse existing TaskModel): - add_task(user_id, title, deescription). -lit_tasks(user_id, status?).-complete_task(user_id, yask_id). -update_task(user_id, task_id, title? descriptin?) -delete_task(user_id, ask_id)  --CHAT ENDPOINT(NEW): -POST/api/{user_id}/chat. -Reques: {onversation_id?, message}. -Response: {conversation_id, repinse, tool_calls[] }. --NEW DB MODELS: -Conversaion:id, ser_id, creates_at, updaes_at. -Message: id, conversation_id, user_id, role, contnet, created_at.  --RULES: -No code before all soecs are clete. -reuse eisting JWT middleware from Phase2. -Reuse existing Task model frm Phase 2. -Reuse existig DB Connectin from Phase 2. -user_id ALWAYS from JWT token, rquest body, -All inoyts validated via Pydantic. - Proper HTTP status codes. -envirpmene variabels for all secrets. -User can nly access their own data. - Server is statelss(all states in NEON DB). - Load lat 20 messages as history er request. -Use Gemini aAPI for LLM."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Creation (Priority: P1)

As a user, I want to create tasks by typing natural language messages like "add buy groceries" or "remember to call mom" so that I can quickly capture tasks without navigating through forms or buttons.

**Why this priority**: This is the core value proposition of the AI chatbot - enabling frictionless task capture through conversation. Without this, the chatbot provides no advantage over the existing web interface.

**Independent Test**: Can be fully tested by sending a chat message "add buy milk" and verifying a new task appears in the user's task list with the title "buy milk".

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with an active chat session, **When** I send the message "add buy groceries", **Then** a new task titled "buy groceries" is created in my task list
2. **Given** I am an authenticated user, **When** I send "remember to call the dentist tomorrow", **Then** a new task is created with the title "call the dentist tomorrow"
3. **Given** I am an authenticated user, **When** I send "create a task to finish the quarterly report", **Then** a new task is created with appropriate title extracted from the message
4. **Given** I am an authenticated user, **When** I send an ambiguous message like "hello", **Then** the chatbot responds with a helpful message explaining available commands without creating a task
5. **Given** I am an authenticated user, **When** I send "add task with description: buy milk and eggs for breakfast", **Then** a task is created with both title and description properly extracted

---

### User Story 2 - View Tasks via Conversation (Priority: P1)

As a user, I want to view my tasks by asking questions like "show my tasks" or "what do I need to do today?" so that I can review my todo list through natural conversation.

**Why this priority**: Viewing tasks is equally critical as creating them - users need to see what they've captured. This completes the basic read/write cycle and makes the chatbot useful.

**Independent Test**: Can be fully tested by creating a few tasks, then sending "show my tasks" and verifying the chatbot returns a formatted list of all tasks.

**Acceptance Scenarios**:

1. **Given** I have 3 pending tasks in my list, **When** I send "show my tasks", **Then** the chatbot displays all 3 tasks with their titles and status
2. **Given** I have no tasks, **When** I send "list my todos", **Then** the chatbot responds with "You have no tasks at the moment"
3. **Given** I have 5 tasks (2 completed, 3 pending), **When** I send "what are my pending tasks?", **Then** the chatbot shows only the 3 pending tasks
4. **Given** I have tasks, **When** I send "show completed tasks", **Then** the chatbot displays only completed tasks with their completion information

---

### User Story 3 - Mark Tasks Complete via Chat (Priority: P2)

As a user, I want to mark tasks as done by saying things like "done with groceries" or "mark buy milk as complete" so that I can update task status conversationally without switching to the web interface.

**Why this priority**: Completing tasks is essential for task management, but users can still get significant value from creating and viewing tasks without this feature initially. They could fall back to the web UI for completion.

**Independent Test**: Can be fully tested by creating a task "buy milk", then sending "mark buy milk as complete" and verifying the task status changes to completed.

**Acceptance Scenarios**:

1. **Given** I have a pending task "buy groceries", **When** I send "done with buy groceries", **Then** the task is marked as completed
2. **Given** I have a pending task "call dentist", **When** I send "mark call dentist as complete", **Then** the task status changes to completed
3. **Given** I have a pending task "write report", **When** I send "finished write report", **Then** the task is marked as done and the chatbot confirms the action
4. **Given** I reference a non-existent task, **When** I send "done with xyz", **Then** the chatbot responds with "I couldn't find a task matching 'xyz'. Would you like to see your current tasks?"

---

### User Story 4 - Update Task Details via Chat (Priority: P3)

As a user, I want to modify existing tasks by saying "change groceries to buy milk and bread" or "update report task description" so that I can refine tasks without deleting and recreating them.

**Why this priority**: Updating is a convenience feature that enhances user experience but isn't critical for initial value delivery. Users can work around this by using the web interface or deleting and recreating tasks.

**Independent Test**: Can be fully tested by creating a task "groceries", then sending "change groceries to buy milk and eggs" and verifying the task title updates.

**Acceptance Scenarios**:

1. **Given** I have a task "groceries", **When** I send "change groceries to buy milk and eggs", **Then** the task title updates to "buy milk and eggs"
2. **Given** I have a task "report", **When** I send "update report description to include Q1 data analysis", **Then** the task description is updated accordingly
3. **Given** I have a task "call dentist", **When** I send "rename call dentist to call dentist at 3pm Friday", **Then** the task title is updated
4. **Given** I reference a non-existent task, **When** I send "change xyz to abc", **Then** the chatbot responds with an error message and suggests viewing current tasks

---

### User Story 5 - Delete Tasks via Chat (Priority: P3)

As a user, I want to remove tasks by saying "delete groceries" or "remove the dentist task" so that I can clean up my task list conversationally.

**Why this priority**: Deletion is useful but not critical for initial value delivery. Users can work around this by completing tasks instead or using the web interface for deletion.

**Independent Test**: Can be fully tested by creating a task "test task", then sending "delete test task" and verifying it no longer appears in the task list.

**Acceptance Scenarios**:

1. **Given** I have a task "buy milk", **When** I send "delete buy milk", **Then** the task is permanently removed from my list and the chatbot confirms the deletion
2. **Given** I have a task "call mom", **When** I send "remove call mom", **Then** the task is deleted
3. **Given** I have a task "groceries", **When** I send "cancel groceries task", **Then** the task is removed
4. **Given** I reference a non-existent task, **When** I send "delete xyz", **Then** the chatbot responds with "I couldn't find a task named 'xyz' to delete"

---

### User Story 6 - Persistent Conversation Context (Priority: P2)

As a user, I want the chatbot to remember our conversation history across sessions so that I can have natural, contextual interactions without repeating myself every time I return.

**Why this priority**: Context persistence enables natural conversation flow and significantly improves user experience, making the chatbot feel intelligent and helpful. However, basic task operations can work without it.

**Independent Test**: Can be fully tested by having a conversation, closing the session, reopening, and verifying the chatbot remembers previous context (last 20 messages).

**Acceptance Scenarios**:

1. **Given** I had a conversation yesterday where I created 3 tasks, **When** I start a new session today and ask "what did we talk about yesterday?", **Then** the chatbot can reference our previous conversation
2. **Given** I asked "show my tasks" in a previous message and the bot listed 5 tasks, **When** I say "mark the first one as done", **Then** the chatbot understands which task I'm referring to from context
3. **Given** I'm in the middle of a conversation, **When** I close and reopen the chat, **Then** the conversation history (last 20 messages) is preserved and loaded
4. **Given** I switch devices, **When** I log in on a new device, **Then** my conversation history is available and continues seamlessly

---

### User Story 7 - Multi-Turn Conversation Flow (Priority: P2)

As a user, I want to have natural back-and-forth conversations with the chatbot where it asks clarifying questions when needed, so that I can provide information naturally rather than in rigid command formats.

**Why this priority**: Multi-turn conversations make the chatbot feel more natural and intelligent, improving user satisfaction. However, single-turn commands can still provide core functionality.

**Independent Test**: Can be fully tested by sending an ambiguous command like "add task" and verifying the chatbot asks "What would you like the task to be?" before creating it.

**Acceptance Scenarios**:

1. **Given** I am in a chat session, **When** I send "add task", **Then** the chatbot responds "What would you like the task to be?" and waits for my next message
2. **Given** the chatbot asked me for clarification, **When** I provide the missing information in my next message, **Then** the chatbot completes the original action using the context
3. **Given** I send an incomplete command like "update task", **When** the chatbot asks "Which task would you like to update?", **Then** I can respond with the task name in the next message
4. **Given** I'm having a multi-turn conversation, **When** I change topics mid-conversation, **Then** the chatbot adapts and handles the new request appropriately

---

### Edge Cases

- What happens when a user sends a message that doesn't match any known command pattern (e.g., "how's the weather?")? → System MUST respond with helpful guidance about available commands without attempting tool calls
- How does the system handle ambiguous task references when multiple tasks have similar names (e.g., "delete the report task" when there are 3 tasks with "report" in the title)? → System MUST ask for clarification or list matching tasks for user to choose from
- What happens when a user tries to complete or delete a task that doesn't exist? → System MUST return user-friendly error message via tool output and inform user in natural language
- How does the system handle very long messages (e.g., 5000+ characters)? → System MUST validate message length (max 5000 chars) and return 400 Bad Request with validation error
- What happens when the Gemini API is unavailable or returns an error? → System MUST catch exception, return 503 Service Unavailable with message "AI service temporarily unavailable. Please try again."
- How does the system handle concurrent chat requests from the same user in multiple browser tabs? → System MUST handle independently (stateless design), each request loads latest 20 messages from DB
- What happens when a user's JWT token expires mid-conversation? → System MUST return 401 Unauthorized, frontend MUST prompt re-authentication
- How does the system handle special characters, emojis, or non-English text in messages? → System MUST accept UTF-8 encoded text, Gemini processes as-is (may have reduced accuracy for non-English)
- What happens when a user tries to access a conversation that belongs to another user? → System MUST return 403 Forbidden after checking conversation.user_id against JWT user_id
- How does the system handle database connection failures during a chat request? → System MUST catch DB exceptions, return 500 Internal Server Error with generic message, log detailed error server-side
- What happens when conversation history exceeds 20 messages - how is the context window managed? → System MUST load only last 20 messages ordered by created_at DESC, older messages remain in DB but not loaded into context
- How does the system handle rapid-fire messages sent in quick succession? → System MUST process each request independently (stateless), may result in race conditions for conversation history (acceptable for MVP)
- What happens when a tool call fails (e.g., database error when creating a task)? → MCP tool MUST return success: false with error message, agent includes this in response to user
- How does the system handle malformed or injection attempts in user messages? → Pydantic validates request schema, Gemini processes as natural language (no direct SQL/code execution risk), MCP tools validate inputs
- What happens when OpenAI Agents SDK fails to initialize or crashes? → System MUST catch initialization errors, return 500 Internal Server Error, log error for debugging
- How does the system handle missing or invalid conversation_id in request? → If invalid UUID format: 400 Bad Request. If valid UUID but not found: 404 Not Found. If omitted: create new conversation
- What happens when user_id cannot be extracted from JWT token? → JWT middleware MUST reject request with 401 Unauthorized before reaching chat endpoint
- How does the system handle tool calls that require parameters not provided by user? → Agent MUST ask clarifying questions in multi-turn conversation before invoking tool
- What happens when Gemini returns a response but fails to invoke required tools? → System MUST return response as-is with empty tool_calls array, user may need to rephrase
- How does the system handle database migration failures when adding Conversation/Message tables? → Migration MUST be tested in staging, rollback plan required, application startup MUST fail if tables missing

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept natural language input via a chat endpoint and interpret user intent for task management operations using Gemini API
- **FR-002**: System MUST support creating tasks from natural language phrases indicating task creation intent via MCP tool `add_task`
- **FR-003**: System MUST support listing tasks from natural language queries requesting task information via MCP tool `list_tasks`
- **FR-004**: System MUST support marking tasks complete from natural language phrases indicating completion via MCP tool `complete_task`
- **FR-005**: System MUST support updating task details from natural language phrases indicating modification via MCP tool `update_task`
- **FR-006**: System MUST support deleting tasks from natural language phrases indicating removal via MCP tool `delete_task`
- **FR-007**: System MUST extract user identity exclusively from JWT authentication tokens, never from request body (reuse Phase 2 JWT middleware)
- **FR-008**: System MUST persist all conversation messages to a database for context retention in new Message table
- **FR-009**: System MUST load the last 20 messages from conversation history on every request to maintain context
- **FR-010**: System MUST maintain separate conversation histories for each user in new Conversation table
- **FR-011**: System MUST operate statelessly with zero in-memory session state (all state in Neon DB)
- **FR-012**: System MUST return structured responses containing conversation_id, response text, and tool_calls array
- **FR-013**: System MUST handle all errors gracefully with user-friendly messages that don't expose system internals
- **FR-014**: System MUST return 401 status when JWT token is missing or invalid
- **FR-015**: System MUST return 403 status when user attempts to access conversations or tasks belonging to another user
- **FR-016**: System MUST use Gemini API (gemini-2.0-flash) for natural language understanding and response generation (NOT OpenAI GPT models)
- **FR-017**: System MUST provide five distinct MCP tool functions for task operations that reuse existing Task models: add_task, list_tasks, complete_task, update_task, delete_task
- **FR-018**: System MUST validate all inputs using Pydantic models
- **FR-019**: System MUST store conversation and message data in the Neon PostgreSQL database
- **FR-020**: System MUST associate each conversation with a single user via user_id foreign key
- **FR-021**: System MUST preserve conversation context across multiple sessions
- **FR-022**: System MUST respond helpfully when user input doesn't match any known command pattern
- **FR-023**: System MUST reuse existing JWT authentication middleware from Phase 2 without modification
- **FR-024**: System MUST reuse existing Task model and database schema from Phase 2 without modification
- **FR-025**: System MUST reuse existing database connection from Phase 2 (backend/db.py)
- **FR-026**: System MUST use proper HTTP status codes for all responses (200, 400, 401, 403, 404, 500, 503)
- **FR-027**: System MUST store all secrets and API keys in environment variables (GEMINI_API_KEY, BETTER_AUTH_SECRET, DATABASE_URL)
- **FR-028**: System MUST ensure users can only access their own conversations and tasks
- **FR-029**: System MUST support optional conversation_id in requests to continue existing conversations
- **FR-030**: System MUST create a new conversation when conversation_id is not provided
- **FR-031**: System MUST include tool call results in the response when tools are invoked
- **FR-032**: System MUST handle multi-turn conversations where context from previous messages informs current responses
- **FR-033**: System MUST use OpenAI Agents SDK for agent loop and tool orchestration
- **FR-034**: System MUST define all tools using Official MCP Python SDK with proper schemas
- **FR-035**: System MUST integrate OpenAI Chatkit (or equivalent) for frontend chat UI
- **FR-036**: System MUST validate MCP tool inputs against defined JSON schemas before execution
- **FR-037**: System MUST return tool execution results in tool_calls array with tool_name, input, output, and success fields
- **FR-038**: System MUST handle Gemini API failures with 503 status and user-friendly error messages
- **FR-039**: System MUST automatically inject user_id from JWT token into all MCP tool calls
- **FR-040**: System MUST create database indexes on conversations(user_id, updated_at) and messages(conversation_id, created_at)

### Key Entities

- **Conversation**: Represents a chat session between a user and the AI chatbot. Contains a unique identifier, the user who owns it, and timestamps for creation and last update. A user can have multiple conversations over time. Each conversation maintains its own message history.

- **Message**: Represents a single message within a conversation. Contains a unique identifier, the conversation it belongs to, the user who owns it, the role (user or assistant), the message content, and creation timestamp. Messages are ordered chronologically within a conversation to maintain context.

- **Task**: Represents a todo item (from Phase 2). Contains a unique identifier, the user who owns it, title, optional description, status (pending/completed), and timestamps. Tasks are managed through both the web interface and the chatbot interface.

- **User**: Represents an authenticated user (from Phase 2). Identified by user_id from JWT token. Owns conversations and tasks. Authentication and authorization are handled by existing Phase 2 middleware.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task in under 10 seconds by typing a single natural language message
- **SC-002**: Users can view their complete task list in under 5 seconds by asking a natural language question
- **SC-003**: The chatbot correctly interprets user intent for task operations with at least 85% accuracy for common phrasings
- **SC-004**: The system maintains conversation context across sessions, allowing users to reference previous messages within the last 20 message window
- **SC-005**: The system handles 100 concurrent users without performance degradation or response delays
- **SC-006**: All chat requests complete within 3 seconds under normal load (excluding AI processing time)
- **SC-007**: The system gracefully handles AI service failures with user-friendly error messages in 100% of cases
- **SC-008**: 90% of users successfully complete their first task creation via chat on the first attempt
- **SC-009**: The system prevents unauthorized access with 100% accuracy (no user can access another user's conversations or tasks)
- **SC-010**: Conversation history persists indefinitely and is retrievable across any number of sessions
- **SC-011**: Users report higher satisfaction with task management when using the chatbot compared to the web interface alone
- **SC-012**: The chatbot reduces the average time to complete common task management operations by at least 30% compared to the web interface

## Technical Architecture

### Stack Components (Phase 3 Additions)

#### AI Agent Orchestration
- **OpenAI Agents SDK**: Provides agent loop and tool orchestration framework
  - Agent loop manages conversation flow and tool invocation
  - Handles multi-turn conversations with context management
  - Orchestrates tool calls based on user intent
  - Manages agent state and conversation history

#### Language Model
- **Gemini API (gemini-2.0-flash)**: Primary LLM for natural language understanding and generation
  - **NOT using OpenAI GPT models** - Gemini only
  - Processes user messages to determine intent
  - Generates natural language responses
  - Decides which tools to invoke based on conversation context
  - API endpoint: Google AI Studio / Vertex AI
  - Model: `gemini-2.0-flash-exp` or latest stable 2.0 variant

#### Tool Integration
- **Official MCP Python SDK**: Provides standardized tool interface
  - Defines tool schemas and contracts
  - Handles tool registration and invocation
  - Validates tool inputs and outputs
  - Provides error handling for tool failures

#### Frontend Chat UI
- **OpenAI Chatkit**: Pre-built React chat interface components
  - Message display with user/assistant roles
  - Input field with send button
  - Loading states during AI processing
  - Error message display
  - Conversation history rendering

### MCP Tool Specifications

All tools reuse the existing Task model from Phase 2 (`backend/models.py`). Each tool is exposed via the MCP Python SDK with the following contracts:

#### Tool 1: add_task
**Purpose**: Create a new task for the authenticated user

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID from JWT token (automatically injected)"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Task title extracted from user message"
    },
    "description": {
      "type": "string",
      "maxLength": 2000,
      "description": "Optional task description",
      "default": ""
    }
  },
  "required": ["user_id", "title"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "task": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "completed": {"type": "boolean"},
        "created_at": {"type": "string", "format": "date-time"}
      }
    },
    "error": {
      "type": "string",
      "description": "Error message if success is false"
    }
  }
}
```

#### Tool 2: list_tasks
**Purpose**: Retrieve tasks for the authenticated user with optional status filter

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID from JWT token (automatically injected)"
    },
    "status": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "default": "all",
      "description": "Filter tasks by completion status"
    }
  },
  "required": ["user_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "title": {"type": "string"},
          "description": {"type": "string"},
          "completed": {"type": "boolean"},
          "created_at": {"type": "string", "format": "date-time"},
          "updated_at": {"type": "string", "format": "date-time"}
        }
      }
    },
    "count": {
      "type": "integer",
      "description": "Total number of tasks returned"
    },
    "error": {
      "type": "string"
    }
  }
}
```

#### Tool 3: complete_task
**Purpose**: Mark a task as completed

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID from JWT token (automatically injected)"
    },
    "task_id": {
      "type": "string",
      "description": "ID of the task to mark complete"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "task": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "completed": {"type": "boolean"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    },
    "error": {
      "type": "string"
    }
  }
}
```

#### Tool 4: update_task
**Purpose**: Update task title and/or description

**Input Schema**:
```json
{
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
      "minLength": 1,
      "maxLength": 200,
      "description": "New task title (optional)"
    },
    "description": {
      "type": "string",
      "maxLength": 2000,
      "description": "New task description (optional)"
    }
  },
  "required": ["user_id", "task_id"],
  "minProperties": 3
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "task": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "completed": {"type": "boolean"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    },
    "error": {
      "type": "string"
    }
  }
}
```

#### Tool 5: delete_task
**Purpose**: Permanently delete a task

**Input Schema**:
```json
{
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
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "message": {
      "type": "string",
      "description": "Confirmation message"
    },
    "error": {
      "type": "string"
    }
  }
}
```

### Chat Endpoint Specification

#### Endpoint: POST /api/v1/chat

**Purpose**: Accept user messages, process with AI agent, invoke tools, and return responses

**Authentication**: Required (JWT token in Authorization header)

**Request Schema**:
```json
{
  "type": "object",
  "properties": {
    "conversation_id": {
      "type": "string",
      "format": "uuid",
      "description": "Optional. If provided, continues existing conversation. If omitted, creates new conversation."
    },
    "message": {
      "type": "string",
      "minLength": 1,
      "maxLength": 5000,
      "description": "User's message text"
    }
  },
  "required": ["message"]
}
```

**Request Example**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "add buy groceries"
}
```

**Response Schema**:
```json
{
  "type": "object",
  "properties": {
    "conversation_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of the conversation (new or existing)"
    },
    "response": {
      "type": "string",
      "description": "AI-generated response text"
    },
    "tool_calls": {
      "type": "array",
      "description": "List of tools invoked during this request",
      "items": {
        "type": "object",
        "properties": {
          "tool_name": {
            "type": "string",
            "enum": ["add_task", "list_tasks", "complete_task", "update_task", "delete_task"]
          },
          "input": {
            "type": "object",
            "description": "Input parameters passed to the tool"
          },
          "output": {
            "type": "object",
            "description": "Result returned by the tool"
          },
          "success": {
            "type": "boolean"
          }
        }
      }
    },
    "message_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of the assistant's message"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["conversation_id", "response", "tool_calls"]
}
```

**Response Example (Success)**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "I've added 'buy groceries' to your task list.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "input": {
        "user_id": "user_123",
        "title": "buy groceries"
      },
      "output": {
        "success": true,
        "task": {
          "id": "task_456",
          "title": "buy groceries",
          "description": "",
          "completed": false,
          "created_at": "2026-04-25T11:28:05.840Z"
        }
      },
      "success": true
    }
  ],
  "message_id": "msg_789",
  "timestamp": "2026-04-25T11:28:06.123Z"
}
```

**Error Response Schema**:
```json
{
  "type": "object",
  "properties": {
    "error": {
      "type": "string",
      "description": "Error message"
    },
    "error_code": {
      "type": "string",
      "enum": ["INVALID_TOKEN", "CONVERSATION_NOT_FOUND", "AI_SERVICE_ERROR", "VALIDATION_ERROR", "UNAUTHORIZED"]
    },
    "status": {
      "type": "integer",
      "enum": [400, 401, 403, 404, 500, 503]
    }
  }
}
```

**HTTP Status Codes**:
- `200 OK`: Request processed successfully
- `400 Bad Request`: Invalid request body or validation error
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User attempting to access another user's conversation
- `404 Not Found`: Conversation ID not found
- `500 Internal Server Error`: Server error or tool execution failure
- `503 Service Unavailable`: AI service (Gemini API) unavailable

### Database Schema Updates

#### New Table: Conversation
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
```

#### New Table: Message
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

### Integration Flow

1. **User sends message** → Frontend (OpenAI Chatkit) → POST /api/v1/chat
2. **Backend receives request** → JWT middleware extracts user_id
3. **Load conversation history** → Fetch last 20 messages from database
4. **Initialize OpenAI Agents SDK** → Create agent with Gemini LLM and MCP tools
5. **Agent processes message** → Gemini determines intent and tool calls
6. **Execute tools** → MCP SDK invokes tools (add_task, list_tasks, etc.)
7. **Generate response** → Gemini creates natural language response
8. **Persist messages** → Save user message and assistant response to database
9. **Return response** → Send JSON response with conversation_id, response, tool_calls
10. **Frontend displays** → OpenAI Chatkit renders assistant message

### Environment Variables Required

```bash
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# OpenAI Agents SDK (no API key needed, using Gemini as LLM)
# MCP SDK Configuration (no additional env vars needed)

# Existing Phase 2 Variables (reused)
DATABASE_URL=postgresql://user:pass@host:5432/taskflow
BETTER_AUTH_SECRET=shared_secret_for_jwt
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15
```

## Assumptions

- Phase 2 JWT authentication middleware is fully functional and can be reused without modification
- Phase 2 Task model and database schema are stable and support all required operations
- Phase 2 database connection is reliable and can handle additional conversation/message tables
- Gemini API credentials and access are available and configured
- OpenAI Agents SDK can be configured to use Gemini as the LLM (not OpenAI GPT models)
- The database can handle the additional load from storing conversation history
- Users have valid JWT tokens before accessing the chat endpoint
- Gemini can reliably interpret common task management phrases in English
- Network connectivity to Gemini API is generally reliable with acceptable latency
- Task titles and descriptions are sufficient for most use cases
- Users understand that the chatbot operates on natural language and may occasionally misinterpret intent
- The system will use English language for natural language understanding initially
- Conversation history of 20 messages provides sufficient context for most interactions
- The existing Next.js frontend can integrate OpenAI Chatkit components
- Environment variables are properly configured for all secrets and API keys
- MCP Python SDK is compatible with OpenAI Agents SDK for tool orchestration
- OpenAI Chatkit is compatible with the custom chat endpoint response format

## Dependencies

- Phase 2 JWT authentication middleware (backend/utils/auth.py) - MUST reuse existing implementation
- Phase 2 Task model and CRUD operations (backend/models.py, backend/routes/) - MUST reuse existing TaskModel
- Phase 2 database connection (backend/db.py) - MUST reuse existing Neon DB connection
- Phase 2 Next.js frontend application - MUST integrate chat UI into existing app
- Gemini API (gemini-2.0-flash) access and credentials - NEW
- OpenAI Agents SDK for agent loop and tool orchestration - NEW
- Official MCP Python SDK for tool definitions - NEW
- OpenAI Chatkit for frontend chat UI - NEW
- Database support for new Conversation and Message tables - NEW (migration required)
- Python packages: `google-generativeai`, `openai-agents-sdk`, `mcp-python-sdk`
- Frontend packages: `@openai/chatkit` or equivalent React chat component library

## Out of Scope

- Multi-language support (English only for initial release)
- Voice input/output capabilities
- Task scheduling, reminders, or notifications
- Task categories, tags, or labels
- Task priority levels or sorting
- Collaborative tasks or task sharing between users
- Task attachments or file uploads
- Advanced AI features like task suggestions, smart scheduling, or predictive task creation
- Mobile-specific optimizations or native mobile apps
- Offline mode or local-first architecture
- Task search functionality beyond natural language queries
- Bulk operations (e.g., "delete all completed tasks")
- Task due dates or deadlines
- Task assignment to other users
- Integration with external calendar or task management systems
- Custom AI model training or fine-tuning
- Conversation export or backup features
- Conversation search across all user conversations
- Analytics or insights about task completion patterns
- Conversation branching or multiple conversation threads
