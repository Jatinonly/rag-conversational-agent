import React, { useState } from 'react'
import { FileText, Trash2, CheckCircle, Radio } from 'lucide-react'
import { Button } from '../ui/button'
import { AlertDialog } from '../ui/alert-dialog'
import { cn } from '../../lib/utils'

export function DocumentItem({ document, isSelected, onSelect, onDelete }) {
  const [showConfirmDelete, setShowConfirmDelete] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleDelete = async () => {
    setIsDeleting(true)
    const success = await onDelete(document.document_id)
    setIsDeleting(false)
    if (success) {
      setShowConfirmDelete(false)
    }
  }

  return (
    <>
      <div
        className={cn(
          'group relative flex items-center justify-between p-2.5 rounded-lg border transition-all cursor-pointer text-left',
          isSelected
            ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
            : 'bg-white hover:bg-slate-50 border-slate-200 text-slate-800'
        )}
        onClick={() => onSelect(document.document_id)}
      >
        <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-2">
          <div
            className={cn(
              'p-1.5 rounded-md shrink-0 transition-colors',
              isSelected ? 'bg-slate-800 text-slate-200' : 'bg-slate-100 text-slate-600'
            )}
          >
            <FileText className="h-4 w-4" />
          </div>

          <div className="min-w-0 flex-1">
            <p className={cn('text-xs font-medium truncate', isSelected ? 'text-white' : 'text-slate-800')}>
              {document.filename}
            </p>
            <p
              className={cn(
                'text-[10px] font-mono truncate',
                isSelected ? 'text-slate-400' : 'text-slate-400'
              )}
            >
              ID: {document.document_id.slice(0, 8)}...
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0">
          {isSelected && (
            <span className="text-[10px] font-medium bg-slate-800 text-slate-200 px-1.5 py-0.5 rounded-sm">
              Active
            </span>
          )}

          <Button
            type="button"
            variant="ghost"
            size="icon"
            className={cn(
              'h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity p-0',
              isSelected ? 'text-slate-400 hover:text-white hover:bg-slate-800' : 'text-slate-400 hover:text-red-600 hover:bg-red-50'
            )}
            onClick={(e) => {
              e.stopPropagation()
              setShowConfirmDelete(true)
            }}
            title="Delete document"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      <AlertDialog
        open={showConfirmDelete}
        onOpenChange={setShowConfirmDelete}
        title="Delete Document"
        description={`Are you sure you want to delete "${document.filename}"? This will remove its vectors and chunks from SQLite and the FAISS index.`}
        confirmText="Delete Document"
        isDestructive={true}
        isLoading={isDeleting}
        onConfirm={handleDelete}
      />
    </>
  )
}

