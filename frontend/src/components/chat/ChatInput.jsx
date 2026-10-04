import React, { useState, useRef, useEffect } from 'react'
import { Send, Loader2, FileText, Globe } from 'lucide-react'
import { Button } from '../ui/button'
import { Textarea } from '../ui/textarea'

export function ChatInput({ onSendMessage, isQuerying, selectedDoc, hasDocuments }) {
  const [input, setInput] = useState('')
  const textareaRef = useRef(null)

  const handleSubmit = (e) => {
    e?.preventDefault()
    if (!input.trim() || isQuerying) return

    onSendMessage(input)
    setInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e) => {
    // Enter without Shift -> Send
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleChange = (e) => {
    setInput(e.target.value)
    // Auto-grow height up to 160px
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`
    }
  }

  useEffect(() => {
    if (!isQuerying && textareaRef.current) {
      textareaRef.current.focus()
    }
  }, [isQuerying])

  return (
    <div className="border-t border-slate-200 bg-white/80 backdrop-blur-md p-3 sm:p-4">
      <div className="max-w-4xl mx-auto space-y-2">
        {/* Context indicator */}
        <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
          <div className="flex items-center gap-1.5 truncate">
            {selectedDoc ? (
              <>
                <FileText className="h-3 w-3 text-slate-700" />
                <span className="text-slate-600">Retrieval scope:</span>
                <span className="font-semibold text-slate-900 truncate">
                  {selectedDoc.filename}
                </span>
              </>
            ) : (
              <>
                <Globe className="h-3 w-3 text-slate-500" />
                <span className="text-slate-600">Retrieval scope:</span>
                <span className="font-medium text-slate-800">
                  {hasDocuments ? 'All uploaded documents' : 'No documents indexed'}
                </span>
              </>
            )}
          </div>
          <span className="hidden sm:inline text-slate-400">
            Press <kbd className="px-1 py-0.5 rounded bg-slate-100 border border-slate-200 text-[10px]">Enter</kbd> to send, <kbd className="px-1 py-0.5 rounded bg-slate-100 border border-slate-200 text-[10px]">Shift+Enter</kbd> for newline
          </span>
        </div>

        <form onSubmit={handleSubmit} className="relative flex items-end gap-2">
          <Textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={
              hasDocuments
                ? 'Ask a question about your documents...'
                : 'Upload a PDF document first to ask questions...'
            }
            disabled={isQuerying}
            className="min-h-[46px] max-h-40 py-3 pr-12 text-sm leading-relaxed rounded-xl border-slate-200 bg-slate-50/50 focus:bg-white transition-colors"
          />

          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || isQuerying}
            className="absolute right-2 bottom-2 h-8 w-8 rounded-lg bg-slate-900 hover:bg-slate-800 text-white shrink-0 disabled:opacity-40"
          >
            {isQuerying ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  )
}

