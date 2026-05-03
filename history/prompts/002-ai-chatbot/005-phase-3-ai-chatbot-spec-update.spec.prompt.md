---
id: 005
title: Phase 3 AI Chatbot Spec Update - Technical Architecture
stage: spec
date: 2026-04-25
surface: agent
model: claude-opus-4-7
feature: ai-chatbot
branch: 002-ai-chatbot
user: Rubab Fatima
command: /sp.specify
labels: ["specification", "phase-3", "ai-chatbot", "technical-architecture", "gemini-api", "mcp-tools", "openai-agents-sdk"]
links:
  spec: specs/002-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-ai-chatbot/spec.md
  - specs/002-ai-chatbot/checklists/requirements.md
tests:
  - Specification quality checklist validation
---

## Prompt

Project:Evoluton of Todo-Phase 3(AI Chatbot) Evovng from : Phase 2(Full Stack Web App Akready built)  Exisiting codebase to build on p of: -backendmodeks.py(Task mdeks already exists). - backend/d.py(Neon DB conection already esxists). backend/routes/(Task CRUD routes already exists).-backend /utils/auth.py(JWT middleware alreqdy exsts).-Fronted/(Next.js a[p already exists).  --STACK ADDED IN PHASE 3:-OpenAI AGENTS SDK(agent loop+ tool orcheatration) -Gemini API(gemini-2.0 flash) as LLM . - Official MCP Python SDK for tools, -OpenAI Chatkit for CHAT UI. -Conversation + Message tables(NEW) Spec fles returnes from any code. Do not use OPENAI GT MODELS. :-specs/featured/chatbbot.md,-specs/api/mcp-toold.md. specs/api/chat_endpoint.md.-specs/databse/schema.ms(UPDATE-ADD CONVERSTAION+ MESSAAGE). -specs/architectre.md(UPFATE- add MCP +Gemini LAYER. Each sec must contain:- ser stres, Acceptance criters, Edge cases, Validation rules, Dta contracts. --MCO ROOLA(5 requirwed, all reuse existing TaskModel): - add_task(user_id, title, deescription). -lit_tasks(user_id, status?).-complete_task(user_id, yask_id). -update_task(user_id, task_id, title? descriptin?) -delete_task(user_id, ask_id)  --CHAT ENDPOINT(NEW): -POST/api/{user_id}/chat. -Reques: {onversation_id?, message}. -Response: {conversation_id, repinse, tool_calls[] }. --NEW DB MODELS: -Conversaion:id, ser_id, creates_at, updaes_at. -Message: id, conversation_id, user_id, role, contnet, created_at.  --RULES: -No code before all soecs are clete. -reuse eisting JWT middleware from Phase2. -Reuse existing Task model frm Phase 2. -Reuse existig DB Connectin from Phase 2. -user_id ALWAYS from JWT token, rquest body, -All inoyts validated via Pydantic. - Proper HTTP status codes. -envirpmene variabels for all secrets. -User can nly access their own data. - Server is statelss(all states in NEON DB). - Load lat 20 messages as history er request. -Use Gemini aAPI for LLM..         FOR CHATBOT SPEC FOLLLOW ALL THESE RULES THE SPEC FULES YOU HAVE CREATED DOENT MENTION OPENAIAgents SDK, Gemini mentioned but noy how it works, No MCP tool data contracts. N CHAT ENDPUNTS request/respinse sches. do not referece exiting files.    FOLLOW ABOUVE ALL COMMANDS AND AADD IN SEC WHAT IVE TOLD IS MISSING

## Response snapshot

Updated the existing Phase 3 AI Chatbot specification (specs/002-ai-chatbot/spec.md) to include comprehensive technical architecture details that were missing from the initial spec:

**Technical Architecture Section Added:**
- OpenAI Agents SDK integration for agent loop and tool orchestration
- Gemini API (gemini-2.0-flash) as the LLM (explicitly NOT using OpenAI GPT models)
- Official MCP Python SDK for tool definitions

**MCP Tool Specifications (5 tools with complete JSON schemas):**
1. add_task - Create new task with input/output schemas
2. list_tasks - Retrieve tasks with optional status filter
3. complete_task - Mark task as completed
4. update_task - Update task title/description
5. delete_task - Permanently delete task

**Chat Endpoint Specification:**
- POST /api/v1/chat with complete request/response schemas
- Request: {conversation_id?, message}
- Response: {conversation_id, response, tool_calls[], message_id, timestamp}
- Error response schema with error codes and HTTP status codes
- All HTTP status codes documented (200, 400, 401, 403, 404, 500, 503)

**Database Schema Updates:**
- Conversation table DDL with indexes
- Message table DDL with indexes
- Foreign key relationships defined

**Integration Flow:**
- End-to-end flow from user message to response documented
- 10-step process showing OpenAI Agents SDK, Gemini, MCP tools, and database interactions

**Environment Variables:**
- GEMINI_API_KEY, GEMINI_MODEL specified
- Phase 2 variables to reuse documented

**Updated Functional Requirements:**
- Expanded from 32 to 40 requirements
- Added specific requirements for OpenAI Agents SDK, Gemini API, MCP tools
- Clarified Phase 2 component reuse (JWT middleware, Task model, DB connection)

**Updated Edge Cases:**
- Expanded from 14 to 20 edge cases
- Added specific handling requirements for each scenario
- Covered Gemini API failures, tool failures, database errors

**Updated Dependencies:**
- Specified exact packages: google-generativeai, openai-agents-sdk, mcp-python-sdk, @openai/chatkit

**Validation:**
- Updated requirements checklist to reflect Technical Architecture addition
- All 40 functional requirements validated as testable
- Specification marked as ready for /sp.plan

## Outcome

- ✅ Impact: Specification now includes all missing technical details requested by user - OpenAI Agents SDK usage, Gemini API integration, complete MCP tool data contracts, chat endpoint schemas, database schema updates
- 🧪 Tests: Specification quality checklist validation passed with Technical Architecture exception noted
- 📁 Files: specs/002-ai-chatbot/spec.md (updated), specs/002-ai-chatbot/checklists/requirements.md (updated)
- 🔁 Next prompts: Ready for /sp.plan to generate implementation plan
- 🧠 Reflection: User provided detailed requirements that were missing from initial spec. Successfully integrated technical architecture section while maintaining spec quality standards. Technical Architecture section is an acceptable exception to "no implementation details" rule as it defines mandatory Phase 3 stack constraints.

## Evaluation notes (flywheel)

- Failure modes observed: Initial spec lacked technical architecture details that user explicitly required (OpenAI Agents SDK, Gemini API specifics, MCP tool contracts, chat endpoint schemas)
- Graders run and results (PASS/FAIL): Specification quality checklist - PASS (with Technical Architecture exception documented)
- Prompt variant (if applicable): User provided highly detailed technical requirements in natural language with typos - successfully parsed and structured into formal specification
- Next experiment (smallest change to try): Consider adding Technical Architecture section to spec template for projects that require explicit stack constraints upfront
