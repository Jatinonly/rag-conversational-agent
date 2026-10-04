import React from 'react'
import { MessageSquareText } from 'lucide-react'
import { ConversationItem } from './ConversationItem'

export function ConversationList({
  conversations,
  activeId,
  onSelect,
  onDelete,
}) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider px-1 mb-1.5">
        <span className="flex items-center gap-1.5">
          <MessageSquareText className="h-3.5 w-3.5" />
          Chats ({conversations.length})
        </span>
      </div>

      {conversations.length === 0 ? (
        <div className="p-3 text-center text-xs text-slate-400">
          No conversations yet.
        </div>
      ) : (
        <div className="space-y-0.5 max-h-56 overflow-y-auto pr-0.5">
          {conversations.map((conv) => (
            <ConversationItem
              key={conv.id}
              conversation={conv}
              isActive={activeId === conv.id}
              onSelect={onSelect}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}

