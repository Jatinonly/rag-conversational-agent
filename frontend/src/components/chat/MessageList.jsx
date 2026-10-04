import React, { useEffect, useRef } from 'react'
import { Bot, Sparkles, FileText, ArrowRight, Loader2 } from 'lucide-react'
import { MessageBubble } from './MessageBubble'
import { Skeleton } from '../ui/skeleton'

export function MessageList({
  messages,
  isQuerying,
  hasDocuments,
  onPromptClick,
}) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isQuerying])

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-6 text-center">
        <div className="max-w-md space-y-4">
          <div className="mx-auto h-12 w-12 rounded-2xl bg-slate-900 text-white flex items-center justify-center shadow-md">
            <Bot className="h-6 w-6" />
          </div>

          <div className="space-y-1.5">
            <h2 className="text-lg font-semibold text-slate-900">
              RAG Conversational Assistant
            </h2>
            <p className="text-xs text-slate-500 leading-relaxed">
              Ask questions grounded strictly in your uploaded PDF documents. The
              system uses semantic embeddings, BM25 retrieval, and cross-encoder
              reranking to extract precise answers.
            </p>
          </div>

          {!hasDocuments ? (
            <div className="p-3.5 rounded-xl border border-amber-200 bg-amber-50/70 text-xs text-amber-800 text-left flex items-start gap-2.5">
              <FileText className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">No documents uploaded yet</p>
                <p className="text-[11px] text-amber-700 mt-0.5">
                  Upload a PDF using the sidebar to enable retrieval and answering.
                </p>
              </div>
            </div>
          ) : (
            <div className="pt-2 text-left space-y-2">
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider text-center">
                Try asking
              </p>
              <div className="space-y-1.5">
                {[
                  'What is the summary of the document?',
                  'What are the key points mentioned in the document?',
                  'Can you list the main conclusions?',
                ].map((sample) => (
                  <button
                    key={sample}
                    type="button"
                    onClick={() => onPromptClick && onPromptClick(sample)}
                    className="w-full text-left p-2.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs text-slate-700 transition-colors flex items-center justify-between group cursor-pointer"
                  >
                    <span>{sample}</span>
                    <ArrowRight className="h-3.5 w-3.5 text-slate-400 group-hover:text-slate-700 transition-colors" />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
      <div className="max-w-4xl mx-auto divide-y divide-slate-100">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {/* Loading state while querying */}
        {isQuerying && (
          <div className="flex w-full gap-3 py-4 text-sm animate-in fade-in">
            <div className="h-8 w-8 rounded-full bg-slate-900 text-white flex items-center justify-center shrink-0 shadow-xs">
              <Bot className="h-4 w-4" />
            </div>
            <div className="flex-1 max-w-[80%] rounded-2xl bg-white border border-slate-200/90 rounded-tl-xs p-4 shadow-xs space-y-2.5">
              <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
                <Loader2 className="h-3.5 w-3.5 animate-spin text-slate-600" />
                <span>Searching documents & generating answer...</span>
              </div>
              <Skeleton className="h-4 w-5/6" />
              <Skeleton className="h-4 w-4/6" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}

