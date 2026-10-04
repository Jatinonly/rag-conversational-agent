import { apiClient } from './client'

/**
 * Send a question to the RAG backend.
 * Backend route: POST /query
 * Payload: { conversation_id: string, question: string, document_id?: string | null }
 * Returns: {
 *   question: string,
 *   answer: string,
 *   sources: Array<{ page: number, text: string, filename: string, document_id: string, rerank_score: number }>,
 *   cached: boolean
 * }
 */
export async function queryDocument({ conversation_id, question, document_id = null }) {
  const payload = {
    conversation_id,
    question,
    document_id: document_id || null,
  }

  return apiClient('/query', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

