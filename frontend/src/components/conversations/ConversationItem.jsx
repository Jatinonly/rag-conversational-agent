import React, { useState } from 'react'
import { MessageSquare, Trash2 } from 'lucide-react'
import { Button } from '../ui/button'
import { AlertDialog } from '../ui/alert-dialog'
import { cn } from '../../lib/utils'

export function ConversationItem({ conversation, isActive, onSelect, onDelete }) {
  const [showConfirmDelete, setShowConfirmDelete] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleDelete = async () => {
    setIsDeleting(true)
    const success = await onDelete(conversation.id)
    setIsDeleting(false)
    if (success) {
      setShowConfirmDelete(false)
    }
  }

  return (
    <>
      <div
        className={cn(
          'group relative flex items-center justify-between px-3 py-2 rounded-lg text-xs transition-all cursor-pointer',
          isActive
            ? 'bg-slate-200/80 font-medium text-slate-900 shadow-2xs'
            : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
        )}
        onClick={() => onSelect(conversation.id)}
      >
        <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-1">
          <MessageSquare className={cn('h-3.5 w-3.5 shrink-0', isActive ? 'text-slate-900' : 'text-slate-400')} />
          <span className="truncate">{conversation.title || 'Conversation'}</span>
        </div>

        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-red-600 hover:bg-transparent p-0 shrink-0"
          onClick={(e) => {
            e.stopPropagation()
            setShowConfirmDelete(true)
          }}
          title="Delete conversation"
        >
          <Trash2 className="h-3 w-3" />
        </Button>
      </div>

      <AlertDialog
        open={showConfirmDelete}
        onOpenChange={setShowConfirmDelete}
        title="Delete Conversation"
        description="Are you sure you want to delete this conversation and its chat history?"
        confirmText="Delete Conversation"
        isDestructive={true}
        isLoading={isDeleting}
        onConfirm={handleDelete}
      />
    </>
  )
}

