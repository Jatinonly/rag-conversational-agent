import React, { useCallback } from 'react'
import { AppLayout } from '../components/layout/AppLayout'
import { ChatWindow } from '../components/chat/ChatWindow'
import { useDocuments } from '../hooks/useDocuments'
import { useConversations } from '../hooks/useConversations'
import { useChat } from '../hooks/useChat'

export function ChatPage() {
  const {
    documents,
    selectedDocId,
    toggleSelectDocument,
    isLoadingDocs,
    isUploading,
    uploadResult,
    error: docError,
    clearError: clearDocError,
    clearUploadResult,
    upload,
    removeDoc,
  } = useDocuments()

  const {
    conversations,
    activeConversationId,
    setActiveConversationId,
    startNewChat,
    removeConversation,
    updateTitle,
    isCreating: isCreatingChat,
    error: convError,
    clearError: clearConvError,
  } = useConversations()

  const handleFirstMessage = useCallback(
    (convId, snippet) => {
      updateTitle(convId, snippet)
    },
    [updateTitle]
  )

  const {
    messages,
    isLoadingHistory,
    isQuerying,
    error: chatError,
    clearError: clearChatError,
    sendMessage,
  } = useChat({
    activeConversationId,
    onFirstMessage: handleFirstMessage,
  })

  const selectedDoc = documents.find((d) => d.document_id === selectedDocId)

  const handleSendMessage = (question) => {
    sendMessage(question, selectedDocId)
  }

  // Combined active error message for the chat window
  const activeError = chatError || convError || docError

  const handleClearError = () => {
    if (chatError) clearChatError()
    if (convError) clearConvError()
    if (docError) clearDocError()
  }

  return (
    <AppLayout
      // Conversations
      conversations={conversations}
      activeConversationId={activeConversationId}
      isCreatingChat={isCreatingChat}
      onNewChat={startNewChat}
      onSelectConversation={setActiveConversationId}
      onDeleteConversation={removeConversation}
      // Documents
      documents={documents}
      selectedDocId={selectedDocId}
      isLoadingDocs={isLoadingDocs}
      isUploadingDoc={isUploading}
      uploadResult={uploadResult}
      uploadError={docError}
      onClearUploadResult={clearUploadResult}
      onUploadDoc={upload}
      onSelectDoc={toggleSelectDocument}
      onDeleteDoc={removeDoc}
    >
      <ChatWindow
        messages={messages}
        isQuerying={isQuerying || isLoadingHistory}
        hasDocuments={documents.length > 0}
        selectedDoc={selectedDoc}
        error={activeError}
        onClearError={handleClearError}
        onSendMessage={handleSendMessage}
      />
    </AppLayout>
  )
}
export default ChatPage

