import { useState, useEffect, useCallback } from 'react'
import { createConversation, deleteConversation } from '../api/conversations'

const STORAGE_KEY = 'rag_conversations_list'

function loadSavedConversations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) return parsed
    }
  } catch (e) {
    console.error('Error loading conversations from localStorage:', e)
  }
  return []
}

function saveConversationsToStorage(list) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
  } catch (e) {
    console.error('Error saving conversations to localStorage:', e)
  }
}

export function useConversations() {
  const [conversations, setConversations] = useState(loadSavedConversations)
  const [activeConversationId, setActiveConversationId] = useState(() => {
    const saved = loadSavedConversations()
    return saved.length > 0 ? saved[0].id : null
  })
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    saveConversationsToStorage(conversations)
  }, [conversations])

  // Create a new conversation on the backend
  const startNewChat = useCallback(async () => {
    setIsCreating(true)
    setError(null)
    try {
      const res = await createConversation()
      const newId = res.conversation_id
      const newConv = {
        id: newId,
        title: 'New Chat',
        createdAt: new Date().toISOString(),
      }

      setConversations((prev) => [newConv, ...prev])
      setActiveConversationId(newId)
      return newId
    } catch (err) {
      setError(err.message || 'Failed to create new conversation')
      return null
    } finally {
      setIsCreating(false)
    }
  }, [])

  // Auto-initialize if empty
  useEffect(() => {
    if (conversations.length === 0 && !activeConversationId) {
      startNewChat()
    }
  }, [conversations.length, activeConversationId, startNewChat])

  // Delete conversation
  const removeConversation = async (conversationId) => {
    setError(null)
    try {
      await deleteConversation(conversationId)
      const updated = conversations.filter((c) => c.id !== conversationId)
      setConversations(updated)

      if (activeConversationId === conversationId) {
        if (updated.length > 0) {
          setActiveConversationId(updated[0].id)
        } else {
          // If all deleted, create fresh one
          await startNewChat()
        }
      }
      return true
    } catch (err) {
      setError(err.message || 'Failed to delete conversation')
      return false
    }
  }

  // Update conversation title (e.g. from first user prompt)
  const updateTitle = (conversationId, newTitle) => {
    setConversations((prev) =>
      prev.map((c) => (c.id === conversationId ? { ...c, title: newTitle } : c))
    )
  }

  return {
    conversations,
    activeConversationId,
    setActiveConversationId,
    startNewChat,
    removeConversation,
    updateTitle,
    isCreating,
    error,
    clearError: () => setError(null),
  }
}

