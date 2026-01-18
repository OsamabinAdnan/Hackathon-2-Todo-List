import { getAuthHeaders } from '@/lib/auth';

/**
 * Chat API client functions for the Todo AI Chatbot
 */

export interface ChatMessage {
  conversation_id?: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls?: Array<{
    tool: string;
    parameters: Record<string, any>;
    result: any;
  }>;
}

/**
 * Send a message to the chat API
 */
export async function sendMessage(
  userId: string,
  message: ChatMessage
): Promise<ChatResponse> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/chat`,
    {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(message),
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to send message: ${response.status}`
    );
  }

  const data: ChatResponse = await response.json();
  return data;
}

/**
 * Get conversation history
 */
export async function getConversationHistory(
  userId: string,
  conversationId: string
): Promise<any[]> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/conversations/${conversationId}/messages`,
    {
      method: 'GET',
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to get conversation history: ${response.status}`);
  }

  const data: any[] = await response.json();
  return data;
}

/**
 * Create a new conversation
 */
export async function createConversation(userId: string): Promise<{ id: string }> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/conversations`,
    {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to create conversation: ${response.status}`);
  }

  const data: { id: string } = await response.json();
  return data;
}