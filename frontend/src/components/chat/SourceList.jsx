import React, { useState } from 'react'
import { BookOpen, ChevronDown, ChevronRight, FileText } from 'lucide-react'
import { cn } from '../../lib/utils'

export function SourceList({ sources }) {
  const [expandedIndex, setExpandedIndex] = useState(null)

  if (!sources || sources.length === 0) return null

  const toggleExpand = (idx) => {
    setExpandedIndex((prev) => (prev === idx ? null : idx))
  }

  return (
    <div className="mt-3 pt-3 border-t border-slate-100">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 mb-2">
        <BookOpen className="h-3.5 w-3.5 text-slate-400" />
        <span>Sources ({sources.length})</span>
      </div>

      <div className="space-y-1.5">
        {sources.map((source, index) => {
          const isExpanded = expandedIndex === index
          return (
            <div
              key={`${source.document_id || 'doc'}-${source.page}-${index}`}
              className="rounded-md border border-slate-200/80 bg-slate-50/70 text-xs overflow-hidden transition-colors"
            >
              <button
                type="button"
                onClick={() => toggleExpand(index)}
                className="w-full flex items-center justify-between p-2 text-left hover:bg-slate-100/70 transition-colors"
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <FileText className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                  <span className="font-medium text-slate-700 truncate">
                    {source.filename || 'Document'}
                  </span>
                  <span className="text-slate-400">•</span>
                  <span className="text-slate-600 shrink-0 font-medium">
                    Page {source.page}
                  </span>
                  {typeof source.rerank_score === 'number' && (
                    <span className="text-[10px] text-slate-400 shrink-0 hidden sm:inline">
                      (score: {source.rerank_score.toFixed(3)})
                    </span>
                  )}
                </div>

                <div className="text-slate-400 ml-2 shrink-0">
                  {isExpanded ? (
                    <ChevronDown className="h-3.5 w-3.5" />
                  ) : (
                    <ChevronRight className="h-3.5 w-3.5" />
                  )}
                </div>
              </button>

              {isExpanded && source.text && (
                <div className="p-2.5 pt-1 text-[11px] font-mono text-slate-600 bg-white border-t border-slate-100 leading-relaxed whitespace-pre-wrap max-h-36 overflow-y-auto">
                  {source.text}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

