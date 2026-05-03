---
id: 001
title: AI Chatbot Implementation Plan
stage: plan
date: 2026-04-25
surface: agent
model: claude-opus-4-7
feature: 002-ai-chatbot
branch: 002-ai-chatbot
user: Rubab Fatima
command: /sp.plan
labels: ["planning", "architecture", "ai-chatbot", "gemini-api", "mcp-tools"]
links:
  spec: specs/002-ai-chatbot/spec.md
  ticket: null
  adr: specs/002-ai-chatbot/research.md
  pr: null
files:
 - specs/002-ai-chatbot/plan.md
 - specs/002-ai-chatbot/research.md
 - specs/002-ai-chatbot/data-model.md
 - specs/002-ai-chatbot/contracts/chat-api.yaml
 - specs/002-ai-chatbot/contracts/mcp-tools.md
 - specs/002-ai-chatbot/quickstart.md
 - CLAUDE.md
tests:
 - None (planning phase, no tests written yet)
---

## Prompt

(User provided empty input for /sp.plan command)

## Response snapshot

Executed complete planning workflow for AI-Powered Todo Chatbot (Phase 3):

**Phase 0 - Research (research.md)**:
- Resolved 8 technical unknowns about Gemini API, MCP SDK, and architecture
- Key finding: OpenAI Agents SDK incompatible with Gemini API → custom agent loop required
- Key finding: OpenAI Chatkit not publicly available → use @chatscope/chat-ui-kit-react
- Documented 3 architectural decisions (ADRs)
- Identified dependencies: google-generativeai, @chatscope/chat-ui-kit-react

**Phase 1 - Design**:
- Created data-model.md with Conversation and Message entities
- Designed database migration (non-breaking, adds 2 tables with proper indexes)
- Created OpenAPI 3.0 spec for POST /api/v1/chat endpoint
- Defined 5 MCP tool contracts (add_task, list_tasks, complete_task, update_task, delete_task)
- Generated quickstart.md with setup instructions and troubleshooting guide

**Key Architecture Decisions**:
1. Custom agent loop using Gemini API directly (two-phase: message → tools → response)
2. Stateless backend with all state in Neon DB
3. Last 20 messages loaded per request for context (2000-4000 tokens)
4. User ID injection at agent service layer from JWT token
5. Reuse Phase 2 components (JWT middleware, Task model, DB connection)

**Constitution Check**: ✅ PASS
- All technology stack requirements met
- Security principles satisfied (JWT-based auth, user isolation)
- API-first architecture maintained
- TDD workflow ready for implementation phase
- No blocking violations

## Outcome

- ✅ Impact: Complete implementation plan with 5 design artifacts ready for task generation
- 🧪 Tests: No tests written (planning phase); test strategy documented in quickstart.md
- 📁 Files: Created 6 new files (plan.md, research.md, data-model.md, 2 contracts, quickstart.md); updated CLAUDE.md
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks from this plan
- 🧠 Reflection: Planning phase successfully resolved all technical unknowns. Key insight: OpenAI Agents SDK not compatible with Gemini required architectural pivot to custom agent loop, but this provides better control and simpler implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning workflow executed smoothly with all gates passing.
- Graders run and results (PASS/FAIL): Constitution Check: PASS, Technical Context: PASS, Architecture Decisions: PASS
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Proceed to /sp.tasks to generate actionable implementation tasks with TDD test cases
