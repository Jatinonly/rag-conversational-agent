import React from 'react'
import { Files, Layers, FolderOpen } from 'lucide-react'
import { DocumentItem } from './DocumentItem'
import { Skeleton } from '../ui/skeleton'
import { cn } from '../../lib/utils'

export function DocumentList({
  documents,
  selectedDocId,
  onSelectDoc,
  onDeleteDoc,
  isLoading,
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider px-1">
        <span className="flex items-center gap-1.5">
          <Files className="h-3.5 w-3.5" />
          Documents ({documents.length})
        </span>

        {documents.length > 0 && (
          <button
            type="button"
            onClick={() => onSelectDoc(null)}
            className={cn(
              'text-[11px] font-normal transition-colors px-1.5 py-0.5 rounded cursor-pointer',
              selectedDocId === null
                ? 'bg-slate-200 text-slate-800 font-medium'
                : 'text-slate-500 hover:text-slate-800'
            )}
            title="Search across all uploaded documents"
          >
            All Docs
          </button>
        )}
      </div>

      {isLoading && documents.length === 0 ? (
        <div className="space-y-2 py-1">
          <Skeleton className="h-12 w-full rounded-lg" />
          <Skeleton className="h-12 w-full rounded-lg" />
        </div>
      ) : documents.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-200 p-4 text-center bg-slate-50/50">
          <FolderOpen className="h-6 w-6 text-slate-400 mx-auto mb-1.5" />
          <p className="text-xs font-medium text-slate-600">No documents yet</p>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Upload a PDF above to start indexing chunks.
          </p>
        </div>
      ) : (
        <div className="space-y-1.5 max-h-56 overflow-y-auto pr-0.5">
          {documents.map((doc) => (
            <DocumentItem
              key={doc.document_id}
              document={doc}
              isSelected={selectedDocId === doc.document_id}
              onSelect={onSelectDoc}
              onDelete={onDeleteDoc}
            />
          ))}
        </div>
      )}
    </div>
  )
}

