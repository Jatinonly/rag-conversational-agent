import React from 'react'
import { AlertCircle } from 'lucide-react'
import { MessageList } from './MessageList'
import { ChatInput } from './ChatInput'
import { Alert, AlertDescription } from '../ui/alert'

export function ChatWindow({
  messages,
  isQuerying,
  hasDocuments,
  selectedDoc,
  error,
  onClearError,
  onSendMessage,
}) {
  return (
    <div className="flex-1 flex flex-col h-full bg-slate-50/50 overflow-hidden">
      {/* Error alert banner */}
      {error && (
        <div className="px-4 pt-3 max-w-4xl w-full mx-auto animate-in slide-in-from-top-2">
          <Alert variant="destructive" className="flex items-center justify-between py-2.5 px-3">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <AlertDescription className="text-xs">{error}</AlertDescription>
            </div>
            {onClearError && (
              <button
                type="button"
                onClick={onClearError}
                className="text-red-700 hover:text-red-900 text-xs font-bold px-1"
              >
                ✕
              </button>
            )}
          </Alert>
        </div>
      )}

      {/* Message history */}
      <MessageList
        messages={messages}
        isQuerying={isQuerying}
        hasDocuments={hasDocuments}
        onPromptClick={(sampleText) => onSendMessage(sampleText)}
      />

      {/* Input area */}
      <ChatInput
        onSendMessage={onSendMessage}
        isQuerying={isQuerying}
        selectedDoc={selectedDoc}
        hasDocuments={hasDocuments}
      />
    </div>
  )
}

