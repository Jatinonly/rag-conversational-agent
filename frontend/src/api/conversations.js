import { apiClient } from './client'

/**
 * Create a new conversation on the backend.
 * Backend route: POST /conversations
 * Returns: { conversation_id: string }
 */
export async function createConversation() {
  return apiClient('/conversations', {
    method: 'POST',
  })
}

/**
 * Fetch messages for a specific conversation.
 * Backend route: GET /conversations/{conversation_id}
 * Returns: { conversation_id: string, messages: Array<{ role: string, content: string }> }
 */
export async function getConversation(conversationId) {
  return apiClient(`/conversations/${conversationId}`, {
    method: 'GET',
  })
}

/**
 * Delete a conversation by ID.
 * Backend route: DELETE /conversations/{conversation_id}
 * Returns: { message: string, conversation_id: string }
 */
export async function deleteConversation(conversationId) {
  return apiClient(`/conversations/${conversationId}`, {
    method: 'DELETE',
  })
}

