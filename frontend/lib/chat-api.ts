/**
 * Chat API client for AI chatbot.
 *
 * [Task]: T049
 * [From]: speckit.specify, contracts/chat-api.yaml
 */

import { apiClient } from './api-client';

// ─── Types ──────────────────────────────────────────────────

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ToolCall {
  tool_name: string;
  input: Record<string, unknown>;
  success: boolean;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: ToolCall[];
  message_id?: string;
  timestamp?: string;
}

export interface ConversationSummary {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationListResponse {
  conversations: ConversationSummary[];
  count: number;
}

export interface MessageResponse {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  tool_call_id?: string;
  created_at: string;
}

export interface MessageListResponse {
  messages: MessageResponse[];
  count: number;
}

// ─── API Functions ──────────────────────────────────────────

/**
 * Send a chat message to the AI chatbot.
 */
export async function sendChatMessage(
  message: string,
  conversationId?: string | null
): Promise<ChatResponse> {
  const body: Record<string, string> = { message };
  if (conversationId) {
    body.conversation_id = conversationId;
  }
  return apiClient.post<ChatResponse>('/api/v1/chat', body);
}

/**
 * List user's conversations.
 */
export async function listConversations(): Promise<ConversationListResponse> {
  return apiClient.get<ConversationListResponse>('/api/v1/conversations');
}

/**
 * Get messages from a conversation.
 */
export async function getConversationMessages(
  conversationId: string
): Promise<MessageListResponse> {
  return apiClient.get<MessageListResponse>(
    `/api/v1/conversations/${conversationId}/messages`
  );
}
