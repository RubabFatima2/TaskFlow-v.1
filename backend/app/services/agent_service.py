"""
Agent service for AI chatbot using standard OpenAI SDK with Gemini.

[Task]: T014, T018, T021, T025, T027, T030, T031, T032, T034, T037, T041, T042, T043
[From]: speckit.plan §ADR-001, research.md §1, §4
"""

import json
import logging
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import settings
from app.services.gemini_service import gemini_client
from app.models.message import Message
from app.mcp import tools as mcp_tools

logger = logging.getLogger(__name__)

# Define the tools exactly as OpenAI function specifications
AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title extracted from user message (1-200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description with additional details"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List the user's tasks. Use this when the user wants to see, view, or check their tasks. Can filter by status (all, pending, completed).",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by completion status. Default: all"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed. Use this when the user says they finished, completed, or are done with a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to mark complete. You MUST use list_tasks first to find the task_id if you don't know it."
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title or description. Use this when the user wants to change, modify, or update task details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to update. You MUST use list_tasks first to find the task_id if you don't know it."
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
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Permanently delete a task. Use this when the user wants to remove, delete, or cancel a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to delete. You MUST use list_tasks first to find the task_id if you don't know it."
                    }
                },
                "required": ["task_id"]
            }
        }
    }
]

async def _execute_tool_call(session: AsyncSession, user_id: int, tool_name: str, kwargs: dict) -> dict:
    """Execute a local MCP tool with the injected user_id and session"""
    logger.info(f"Executing tool: {tool_name} with args: {kwargs}")

    if tool_name == "add_task":
        return await mcp_tools.add_task(session, user_id, kwargs.get("title", ""), kwargs.get("description", ""))
    elif tool_name == "list_tasks":
        return await mcp_tools.list_tasks(session, user_id, kwargs.get("status", "all"))
    elif tool_name == "complete_task":
        return await mcp_tools.complete_task(session, user_id, kwargs.get("task_id", 0))
    elif tool_name == "update_task":
        return await mcp_tools.update_task(session, user_id, kwargs.get("task_id", 0), kwargs.get("title"), kwargs.get("description"))
    elif tool_name == "delete_task":
        return await mcp_tools.delete_task(session, user_id, kwargs.get("task_id", 0))
    else:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

async def _load_conversation_history(session: AsyncSession, conversation_id: str, limit: int = 20) -> list[dict]:
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    messages = list(reversed(result.scalars().all()))

    history = []
    for msg in messages:
        if msg.role == "tool":
            history.append({
                "role": "tool",
                "tool_call_id": msg.tool_call_id,
                "content": msg.content
            })
        else:
            history.append({"role": msg.role, "content": msg.content})

    return history

SYSTEM_INSTRUCTIONS = """You are a helpful AI assistant for TaskFlow, a task management application.

Your role is to help users manage their tasks through natural conversation. You can:
- Add new tasks when users tell you what they need to do
- Show their current tasks when they ask
- Mark tasks as complete when they're done
- Update task titles or descriptions when they want changes
- Delete tasks they no longer need

Guidelines:
- Be concise and friendly in your responses
- When a user wants to complete, update, or delete a task by name, first use list_tasks to find the task_id, then perform the action
- If multiple tasks match a user's description, list the options and ask which one they mean
- If the user's intent is unclear or missing required information, ask a clarifying question instead of making assumptions
- When listing tasks, format them in a readable way
- Confirm actions after performing them (e.g., "I've added 'buy groceries' to your tasks")
- If a tool call fails, explain the issue in user-friendly terms and suggest what they can do
- For general conversation (greetings, questions about capabilities), respond naturally without calling tools
- Never expose internal IDs, technical errors, or system details to the user
"""

async def process_message(
    session: AsyncSession,
    user_id: int,
    message: str,
    conversation_id: Optional[str] = None,
) -> dict:
    try:
        input_messages = [{"role": "system", "content": SYSTEM_INSTRUCTIONS}]

        if conversation_id:
            history = await _load_conversation_history(session, conversation_id)
            input_messages.extend(history)

        input_messages.append({"role": "user", "content": message})

        # Step 1: Initial call to Gemini
        response = await gemini_client.chat.completions.create(
            model=settings.GEMINI_MODEL,
            messages=input_messages,
            tools=AVAILABLE_TOOLS,
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        tool_calls_executed = []
        tool_messages_to_save = []

        # Step 2: Check if Gemini wants to call any tools
        if response_message.tool_calls:
            input_messages.append(response_message)  # Add assistant's tool call request to history

            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name

                try:
                    kwargs = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    kwargs = {}

                # Execute the tool locally
                tool_result = await _execute_tool_call(session, user_id, tool_name, kwargs)

                tool_calls_executed.append({
                    "tool_name": tool_name,
                    "input": kwargs,
                    "success": tool_result.get("success", False),
                })

                # Add tool result to conversation
                tool_content = json.dumps(tool_result)
                input_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": tool_content,
                })

                # Store tool message for database persistence
                tool_messages_to_save.append({
                    "tool_call_id": tool_call.id,
                    "content": tool_content,
                })

            # Step 3: Call Gemini again with the tool results to get the final natural language response
            final_response = await gemini_client.chat.completions.create(
                model=settings.GEMINI_MODEL,
                messages=input_messages,
            )
            response_text = final_response.choices[0].message.content
        else:
            # No tool calls, just use the response
            response_text = response_message.content

        return {
            "response": response_text or "I'm sorry, I couldn't process that. Could you try rephrasing?",
            "tool_calls": tool_calls_executed,
            "tool_messages": tool_messages_to_save,
        }

    except Exception as e:
        logger.error(f"Agent service error: {e}", exc_info=True)

        error_msg = str(e).lower()
        if "rate" in error_msg or "429" in error_msg or "resource_exhausted" in error_msg:
            return {"response": "I'm receiving too many requests right now. Please try again in a moment.", "tool_calls": [], "error_code": "RATE_LIMITED"}
        elif "unavailable" in error_msg or "503" in error_msg:
            return {"response": "The AI service is temporarily unavailable. Please try again shortly.", "tool_calls": [], "error_code": "AI_SERVICE_ERROR"}
        elif "timeout" in error_msg or "504" in error_msg:
            return {"response": "The request timed out. Please try again.", "tool_calls": [], "error_code": "TIMEOUT"}
        else:
            return {"response": "I encountered an error processing your message. Please try again.", "tool_calls": [], "error_code": "INTERNAL_ERROR"}
