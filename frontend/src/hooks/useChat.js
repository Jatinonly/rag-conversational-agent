import { useState, useEffect, useCallback } from 'react'
import { getConversation } from '../api/conversations'
import { queryDocument } from '../api/query'

export function useChat({ activeConversationId, onFirstMessage }) {
  const [messages, setMessages] = useState([])
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)
  const [isQuerying, setIsQuerying] = useState(false)
  const [error, setError] = useState(null)

  // Load conversation history when activeConversationId changes
  const loadHistory = useCallback(async (convId) => {
    if (!convId) {
      setMessages([])
      return
    }

    setIsLoadingHistory(true)
    setError(null)
    try {
      const data = await getConversation(convId)
      if (data && Array.isArray(data.messages)) {
        // Map to format with unique id
        const mapped = data.messages.map((m, idx) => ({
          id: `history-${idx}-${Date.now()}`,
          role: m.role,
          content: m.content,
          sources: [],
          cached: false,
        }))
        setMessages(mapped)
      } else {
        setMessages([])
      }
    } catch (err) {
      // If conversation not found on backend (e.g. DB reset), start empty
      console.warn('Could not load history for conversation:', convId, err.message)
      setMessages([])
    } finally {
      setIsLoadingHistory(false)
    }
  }, [])

  useEffect(() => {
    loadHistory(activeConversationId)
  }, [activeConversationId, loadHistory])

  // Send a user question
  const sendMessage = async (question, documentId = null) => {
    if (!question || !question.trim()) return false
    if (!activeConversationId) return false

    const cleanQuestion = question.trim()
    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: cleanQuestion,
      timestamp: new Date().toISOString(),
    }

    const isFirstMsg = messages.length === 0
    setMessages((prev) => [...prev, userMsg])
    setIsQuerying(true)
    setError(null)

    if (isFirstMsg && onFirstMessage) {
      const snippet = cleanQuestion.length > 28 ? cleanQuestion.slice(0, 28) + '...' : cleanQuestion
      onFirstMessage(activeConversationId, snippet)
    }

    try {
      const res = await queryDocument({
        conversation_id: activeConversationId,
        question: cleanQuestion,
        document_id: documentId || null,
      })

      const assistantMsg = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        sources: Array.isArray(res.sources) ? res.sources : [],
        cached: Boolean(res.cached),
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMsg])
      return true
    } catch (err) {
      setError(err.message || 'Failed to retrieve answer')
      return false
    } finally {
      setIsQuerying(false)
    }
  }

  return {
    messages,
    isLoadingHistory,
    isQuerying,
    error,
    clearError: () => setError(null),
    sendMessage,
  }
}

