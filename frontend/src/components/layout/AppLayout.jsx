import React, { useState } from 'react'
import { Sidebar } from './Sidebar'
import { ChatHeader } from './ChatHeader'

export function AppLayout({
  // Conversations
  conversations,
  activeConversationId,
  isCreatingChat,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
  // Documents
  documents,
  selectedDocId,
  isLoadingDocs,
  isUploadingDoc,
  uploadResult,
  uploadError,
  onClearUploadResult,
  onUploadDoc,
  onSelectDoc,
  onDeleteDoc,
  // Main chat window
  children,
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const activeConversation = conversations.find((c) => c.id === activeConversationId)
  const selectedDoc = documents.find((d) => d.document_id === selectedDocId)

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-100 antialiased">
      {/* Desktop Sidebar (hidden on mobile, visible md+) */}
      <div className="hidden md:flex h-full shrink-0">
        <Sidebar
          conversations={conversations}
          activeConversationId={activeConversationId}
          isCreatingChat={isCreatingChat}
          onNewChat={onNewChat}
          onSelectConversation={onSelectConversation}
          onDeleteConversation={onDeleteConversation}
          documents={documents}
          selectedDocId={selectedDocId}
          isLoadingDocs={isLoadingDocs}
          isUploadingDoc={isUploadingDoc}
          uploadResult={uploadResult}
          uploadError={uploadError}
          onClearUploadResult={onClearUploadResult}
          onUploadDoc={onUploadDoc}
          onSelectDoc={onSelectDoc}
          onDeleteDoc={onDeleteDoc}
        />
      </div>

      {/* Mobile Drawer Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-xs md:hidden animate-in fade-in duration-200"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Mobile Drawer Body */}
      <div
        className={`fixed inset-y-0 left-0 z-50 transform md:hidden transition-transform duration-200 ease-in-out ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <Sidebar
          conversations={conversations}
          activeConversationId={activeConversationId}
          isCreatingChat={isCreatingChat}
          onNewChat={onNewChat}
          onSelectConversation={onSelectConversation}
          onDeleteConversation={onDeleteConversation}
          documents={documents}
          selectedDocId={selectedDocId}
          isLoadingDocs={isLoadingDocs}
          isUploadingDoc={isUploadingDoc}
          uploadResult={uploadResult}
          uploadError={uploadError}
          onClearUploadResult={onClearUploadResult}
          onUploadDoc={onUploadDoc}
          onSelectDoc={onSelectDoc}
          onDeleteDoc={onDeleteDoc}
          onCloseMobile={() => setMobileMenuOpen(false)}
        />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        <ChatHeader
          conversationTitle={activeConversation?.title || 'New Chat'}
          selectedDoc={selectedDoc}
          onOpenMobileMenu={() => setMobileMenuOpen(true)}
          onNewChat={onNewChat}
        />

        <main className="flex-1 flex flex-col min-h-0 overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  )
}

