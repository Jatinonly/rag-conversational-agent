import React from 'react'
import { Plus, Loader2 } from 'lucide-react'
import { Button } from '../ui/button'

export function NewChatButton({ onClick, isCreating }) {
  return (
    <Button
      variant="default"
      size="sm"
      className="w-full justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-white font-medium py-2 shadow-xs"
      onClick={onClick}
      disabled={isCreating}
    >
      {isCreating ? (
        <>
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Creating Chat...</span>
        </>
      ) : (
        <>
          <Plus className="h-4 w-4" />
          <span>New Chat</span>
        </>
      )}
    </Button>
  )
}

