import React from 'react'
import { Bot, X, Database, CheckCircle2 } from 'lucide-react'
import { NewChatButton } from '../conversations/NewChatButton'
import { ConversationList } from '../conversations/ConversationList'
import { UploadDocument } from '../documents/UploadDocument'
import { DocumentList } from '../documents/DocumentList'
import { Button } from '../ui/button'

export function Sidebar({
  conversations,
  activeConversationId,
  isCreatingChat,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
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
  onCloseMobile,
}) {
  return (
    <aside className="w-72 sm:w-80 h-full bg-slate-50 border-r border-slate-200 flex flex-col select-none">
      {/* Brand Header */}
      <div className="h-14 border-b border-slate-200 px-4 flex items-center justify-between shrink-0 bg-white">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-slate-900 text-white flex items-center justify-center shadow-xs">
            <Bot className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900 leading-none">RAG Assistant</h2>
            <p className="text-[10px] text-slate-500 font-mono mt-0.5">FastAPI</p>
          </div>
        </div>

        {onCloseMobile && (
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden h-8 w-8 text-slate-500 hover:text-slate-900"
            onClick={onCloseMobile}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Main Sidebar scrollable body */}
      <div className="flex-1 overflow-y-auto p-3 space-y-5">
        {/* New Chat Action */}
        <NewChatButton onClick={onNewChat} isCreating={isCreatingChat} />

        {/* Conversation List */}
        <ConversationList
          conversations={conversations}
          activeId={activeConversationId}
          onSelect={(id) => {
            onSelectConversation(id)
            if (onCloseMobile) onCloseMobile()
          }}
          onDelete={onDeleteConversation}
        />

        {/* Separator */}
        <hr className="border-slate-200" />

        {/* Document Library Section */}
        <div className="space-y-3">
          <UploadDocument
            onUpload={onUploadDoc}
            isUploading={isUploadingDoc}
            uploadResult={uploadResult}
            error={uploadError}
            onClearResult={onClearUploadResult}
          />

          <DocumentList
            documents={documents}
            selectedDocId={selectedDocId}
            onSelectDoc={(id) => {
              onSelectDoc(id)
              if (onCloseMobile) onCloseMobile()
            }}
            onDeleteDoc={onDeleteDoc}
            isLoading={isLoadingDocs}
          />
        </div>
      </div>

      {/* Footer / Status info */}
      <div className="p-3 border-t border-slate-200 bg-white/70 text-[11px] text-slate-500 shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-mono text-[10px] text-slate-600">API: localhost:8000</span>
          </div>
          <span className="text-[10px] text-slate-400">FAISS & BM25</span>
        </div>
      </div>
    </aside>
  )
}

