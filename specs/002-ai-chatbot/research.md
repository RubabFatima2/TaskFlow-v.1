# Research: AI-Powered Todo Chatbot (Phase 3)

**Feature**: 002-ai-chatbot  
**Date**: 2026-04-25  
**Purpose**: Resolve technical unknowns and establish best practices for Gemini API, OpenAI Agents SDK, and MCP Python SDK integration

---

## Research Tasks

### 1. Gemini API Integration with OpenAI Agents SDK
**Question**: How to configure OpenAI Agents SDK to use Gemini API instead of OpenAI GPT models?

**Findings**:
- ✅ **Gemini provides OpenAI-compatible REST API endpoint**
- OpenAI Agents SDK CAN be used with Gemini by overriding the base URL
- Gemini endpoint: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Works by creating AsyncOpenAI client with custom base_url pointing to Gemini
- Supports chat completions interface with same request/response format
- Gemini 2.0 Flash supports function calling (tool use) through OpenAI-compatible interface

**Implementation Pattern**:
```python
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel

# Create OpenAI-compatible client pointing to Gemini
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Define model using Gemini
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Configure runner
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Create and run agent
agent = Agent(name="Assistant", instructions="...", tools=[...])
result = Runner.run_sync(agent, message, run_config=config)
```

**Decision**: Use OpenAI Agents SDK with Gemini via OpenAI-compatible endpoint

**Rationale**: 
- ✅ Follows hackathon spec requirement (OpenAI Agents SDK)
- ✅ Leverages SDK abstractions (agent loop, tool orchestration)
- ✅ Simpler than custom implementation
- ✅ Gemini compatibility layer handles protocol translation
- ✅ Standard agent patterns and error handling built-in

**Limitations**:
- Not native compatibility (uses compatibility layer)
- Potential tool calling inconsistencies
- May have streaming behavior differences
- Good for prototyping and production with testing

**Alternatives Considered**:
- Custom agent loop: More work, reinventing wheel
- LangChain: Too heavy, adds unnecessary complexity
- OpenAI Agents SDK + Gemini: ✅ Chosen - meets spec, simpler, leverages SDK

---

### 2. MCP Python SDK Tool Definition Best Practices
**Question**: How to define MCP tools with proper schemas for Gemini function calling?

**Findings**:
- Official MCP Python SDK provides `@mcp.tool()` decorator for tool registration
- Tool schemas must be JSON Schema compatible
- Gemini function calling expects specific format:
  ```python
  {
    "name": "tool_name",
    "description": "What the tool does",
    "parameters": {
      "type": "object",
      "properties": {...},
      "required": [...]
    }
  }
  ```
- MCP SDK can generate Gemini-compatible schemas from Python type hints
- Best practice: Define Pydantic models for tool inputs/outputs

**Decision**: Use MCP Python SDK with Pydantic models for type-safe tool definitions

**Implementation Pattern**:
```python
from mcp import MCPServer
from pydantic import BaseModel, Field

class AddTaskInput(BaseModel):
    user_id: str = Field(description="User ID from JWT token")
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: str = Field(default="", max_length=2000, description="Optional description")

@mcp.tool()
async def add_task(input: AddTaskInput) -> dict:
    """Create a new task for the authenticated user"""
    # Implementation
    pass
```

**Rationale**:
- Type safety with Pydantic validation
- Automatic schema generation for Gemini
- Clear documentation in code
- Validation errors caught early

---

### 3. Conversation History Management Strategy
**Question**: How to efficiently load and manage last 20 messages for context?

**Findings**:
- PostgreSQL query with ORDER BY created_at DESC LIMIT 20
- Index on (conversation_id, created_at) for fast retrieval
- Messages must be reversed after query (oldest first for Gemini context)
- Gemini context window: 32k tokens (gemini-2.0-flash)
- Average message: ~100-200 tokens
- 20 messages ≈ 2000-4000 tokens (well within limit)

**Decision**: Load last 20 messages per request with database index optimization

**Implementation Pattern**:
```python
# Query (returns newest first)
messages = await db.execute(
    select(Message)
    .where(Message.conversation_id == conv_id)
    .order_by(Message.created_at.desc())
    .limit(20)
)
# Reverse for chronological order (oldest first)
history = list(reversed(messages.scalars().all()))
```

**Rationale**:
- Simple, stateless approach
- Database handles pagination efficiently
- No in-memory caching needed
- Predictable performance

**Alternatives Considered**:
- Redis caching: Premature optimization, adds complexity
- Load all messages: Wastes tokens, slower queries
- Sliding window in memory: Requires stateful backend (violates constitution)

---

### 4. Gemini Function Calling Flow
**Question**: What is the exact flow for Gemini function calling with multi-turn conversations?

**Findings**:
- Gemini function calling is a two-step process:
  1. **First call**: Send message + available functions → Gemini returns function calls
  2. **Second call**: Send function results → Gemini generates natural language response
- Multi-turn conversations require maintaining message history with roles:
  - `user`: User messages
  - `model`: Gemini responses (including function calls)
  - `function`: Function call results
- Gemini API handles function call parsing automatically

**Decision**: Implement two-phase agent loop with function call handling

**Flow**:
```
1. User sends message
2. Load last 20 messages from DB
3. Call Gemini with history + user message + available tools
4. If Gemini returns function calls:
   a. Execute MCP tools
   b. Call Gemini again with function results
   c. Get final natural language response
5. If no function calls:
   a. Use Gemini response directly
6. Save user message and assistant response to DB
7. Return response to user
```

**Rationale**:
- Follows Gemini API best practices
- Handles both tool-using and conversational responses
- Maintains conversation context properly

---

### 5. JWT Token Extraction and User ID Injection
**Question**: How to automatically inject user_id from JWT into all MCP tool calls?

**Findings**:
- FastAPI dependency injection can extract user_id from JWT middleware
- MCP tools should receive user_id as a parameter
- Agent service should inject user_id before calling tools
- Prevents user_id spoofing in tool calls

**Decision**: Use FastAPI dependency injection + agent service wrapper

**Implementation Pattern**:
```python
# In chat endpoint
@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)  # From JWT middleware
):
    # Pass user_id to agent service
    response = await agent_service.process_message(
        user_id=user_id,
        conversation_id=request.conversation_id,
        message=request.message
    )
    return response

# In agent service
async def execute_tool(self, tool_name: str, tool_input: dict, user_id: str):
    # Inject user_id into tool input
    tool_input["user_id"] = user_id
    result = await mcp_tools[tool_name](tool_input)
    return result
```

**Rationale**:
- Security: user_id always from JWT, never from request body
- Simplicity: Tools don't need to handle JWT extraction
- Testability: Easy to mock user_id in tests

---

### 6. Error Handling for AI Service Failures
**Question**: How to gracefully handle Gemini API failures and timeouts?

**Findings**:
- Gemini API can fail due to: rate limits, network issues, service outages, invalid requests
- Recommended timeout: 30 seconds for Gemini API calls
- Retry strategy: Exponential backoff for transient failures (429, 503)
- User-facing errors should be generic, detailed errors logged server-side

**Decision**: Implement try-catch with specific error handling per failure type

**Error Handling Strategy**:
```python
try:
    response = await gemini_client.generate_content(...)
except google.api_core.exceptions.ResourceExhausted:
    # Rate limit exceeded
    raise HTTPException(status_code=429, detail="Too many requests. Please try again in a moment.")
except google.api_core.exceptions.ServiceUnavailable:
    # Gemini service down
    raise HTTPException(status_code=503, detail="AI service temporarily unavailable. Please try again.")
except asyncio.TimeoutError:
    # Request timeout
    raise HTTPException(status_code=504, detail="Request timed out. Please try again.")
except Exception as e:
    # Unexpected error
    logger.error(f"Gemini API error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="An error occurred. Please try again.")
```

**Rationale**:
- User-friendly error messages
- Appropriate HTTP status codes
- Detailed logging for debugging
- No sensitive information exposed

---

### 7. Frontend Chat UI Library Selection
**Question**: What is the best React chat UI library for this use case?

**Findings**:
- **OpenAI Chatkit**: Not publicly available as standalone library (internal OpenAI tool)
- **Alternatives**:
  - `react-chat-elements`: Mature, customizable, 2k+ stars
  - `@chatscope/chat-ui-kit-react`: Modern, TypeScript, well-documented
  - `stream-chat-react`: Full-featured but overkill for simple chat
  - Custom components: Full control, more work

**Decision**: Use `@chatscope/chat-ui-kit-react` for chat UI

**Rationale**:
- TypeScript support (matches Next.js setup)
- Modern, accessible components
- Customizable with Tailwind CSS
- Active maintenance
- Good documentation
- Not tied to specific backend (unlike stream-chat)

**Alternatives Considered**:
- OpenAI Chatkit: Not available publicly
- Custom components: More work, reinventing wheel
- react-chat-elements: Older, less TypeScript support

---

### 8. Database Migration Strategy
**Question**: How to safely add Conversation and Message tables to existing database?

**Findings**:
- Alembic is already configured in Phase 2
- New tables are independent (no changes to existing Task table)
- Foreign key to users table (must exist)
- Indexes needed for performance

**Decision**: Create Alembic migration with proper indexes and constraints

**Migration Checklist**:
- [ ] Create conversations table with user_id foreign key
- [ ] Create messages table with conversation_id and user_id foreign keys
- [ ] Add index on conversations(user_id, updated_at)
- [ ] Add index on messages(conversation_id, created_at)
- [ ] Add CASCADE delete for conversations → messages
- [ ] Test migration in development environment
- [ ] Verify rollback works correctly

**Rationale**:
- Non-breaking change (no existing table modifications)
- Proper foreign key constraints ensure data integrity
- Indexes optimize query performance
- Alembic provides version control for schema changes

---

## Technology Stack Summary

### Backend Dependencies (requirements.txt additions)
```
openai-agents>=0.1.0           # OpenAI Agents SDK
openai>=1.0.0                  # OpenAI client (for AsyncOpenAI)
python-jose[cryptography]>=3.3.0  # JWT verification (existing)
```

**Note**: We use OpenAI Agents SDK with Gemini via OpenAI-compatible endpoint. No need for `google-generativeai` package.

### Frontend Dependencies (package.json additions)
```json
{
  "@chatscope/chat-ui-kit-react": "^2.0.0",
  "@chatscope/chat-ui-kit-styles": "^1.4.0"
}
```

### Environment Variables
```bash
# Backend (.env)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
DATABASE_URL=postgresql://...  # Existing
BETTER_AUTH_SECRET=...         # Existing

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000  # Existing
BETTER_AUTH_SECRET=...         # Existing (must match backend)
```

---

## Architecture Decisions

### ADR-001: Use OpenAI Agents SDK with Gemini via OpenAI-Compatible Endpoint
**Context**: Hackathon spec requires OpenAI Agents SDK. Need to integrate Gemini API for natural language understanding.

**Discovery**: Gemini provides OpenAI-compatible REST API endpoint at `https://generativelanguage.googleapis.com/v1beta/openai/`

**Decision**: Use OpenAI Agents SDK with Gemini by overriding base_url to point to Gemini's OpenAI-compatible endpoint.

**Consequences**:
- ✅ Meets hackathon spec requirement (OpenAI Agents SDK)
- ✅ Leverages SDK abstractions (agent loop, tool orchestration, error handling)
- ✅ Simpler than custom implementation
- ✅ Standard agent patterns built-in
- ⚠️ Uses compatibility layer (not native Gemini SDK)
- ⚠️ Potential tool calling inconsistencies (requires testing)
- ⚠️ May have streaming behavior differences

**Status**: Accepted (Updated 2026-04-25 after discovering Gemini OpenAI-compatible endpoint)

---

### ADR-002: Use @chatscope/chat-ui-kit-react Instead of OpenAI Chatkit
**Context**: OpenAI Chatkit is not publicly available as a standalone library.

**Decision**: Use @chatscope/chat-ui-kit-react for frontend chat UI.

**Consequences**:
- ✅ TypeScript support, modern components
- ✅ Customizable with Tailwind CSS
- ✅ Active maintenance and documentation
- ❌ Need to implement custom API integration
- ❌ Learning curve for new library

**Status**: Accepted

---

### ADR-003: Custom MCP Tool Implementation
**Context**: Official MCP Python SDK may not be mature or available.

**Decision**: If MCP SDK unavailable, implement custom tool registry with JSON Schema validation.

**Consequences**:
- ✅ Full control over tool execution
- ✅ Can optimize for Gemini function calling format
- ❌ More code to maintain
- ❌ Need to implement schema validation manually

**Status**: Conditional (use MCP SDK if available, else custom implementation)

---

## Implementation Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Gemini API rate limits | Medium | High | Implement exponential backoff, user-facing rate limit messages |
| MCP SDK not available/immature | High | Medium | Prepare custom tool implementation as fallback |
| Gemini function calling accuracy | Medium | Medium | Provide clear tool descriptions, handle ambiguous cases with clarifying questions |
| Conversation history token limits | Low | Medium | Monitor token usage, implement truncation if needed |
| Database performance with message history | Low | Medium | Proper indexing, monitor query performance |

---

## Next Steps (Phase 1)

1. Generate data-model.md with Conversation, Message, and Task entities
2. Create API contracts in /contracts/ directory (OpenAPI spec for chat endpoint)
3. Generate quickstart.md with setup instructions
4. Update agent context with new technologies
5. Re-evaluate Constitution Check with design decisions

---

**Research Complete**: All technical unknowns resolved. Ready for Phase 1 design.
